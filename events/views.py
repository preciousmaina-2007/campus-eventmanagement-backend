from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from django_filters import DateFilter, CharFilter
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsOrganizerOrReadOnly
from .models import Event
from .serializers import EventCreateUpdateSerializer, EventSerializer


class EventFilter(FilterSet):
    title = CharFilter(lookup_expr="icontains")
    category = CharFilter(lookup_expr="iexact")
    event_date = DateFilter()
    event_date__gte = DateFilter(field_name="event_date", lookup_expr="gte")
    event_date__lte = DateFilter(field_name="event_date", lookup_expr="lte")

    class Meta:
        model = Event
        fields = ["title", "category", "event_date"]


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    permission_classes = [IsAuthenticated, IsOrganizerOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = EventFilter
    search_fields = ["title", "category"]
    ordering_fields = ["title", "event_date", "created_at", "capacity"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return EventCreateUpdateSerializer
        return EventSerializer

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            EventSerializer(instance, context=self.get_serializer_context()).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    def my_events(self, request):
        """Return events organized by the current user."""
        events = Event.objects.filter(organizer=request.user)
        page = self.paginate_queryset(events)
        if page is not None:
            serializer = EventSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

