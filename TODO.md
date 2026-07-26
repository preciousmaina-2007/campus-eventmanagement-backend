# Testing Progress

## Authentication Tests (`accounts/tests.py`)
- [x] test_user_registration — Successful registration with valid data
- [x] test_registration_password_mismatch — Validation error when passwords don't match
- [x] test_registration_no_role_defaults_to_student — Default role is STUDENT
- [x] test_login — JWT token obtain returns access & refresh tokens
- [x] test_login_invalid_credentials — Reject bad login
- [x] test_token_refresh — Refresh token works
- [x] test_profile_retrieval — Authenticated user can get their profile
- [x] test_profile_unauthenticated — Unauthenticated request to profile returns 401
- [x] test_profile_update — Authenticated user can update username/email
- [x] test_permission_student_role
- [x] test_permission_organizer_role
- [x] test_permission_admin_role
- [x] test_permission_organizer_or_read_only_for_safe_methods
- [x] test_permission_owner_or_admin

## Events CRUD Tests (`events/tests.py`)
- [x] test_list_events — Authenticated user can list events
- [x] test_create_event_as_organizer — Organizer can create an event
- [x] test_create_event_as_student — Student cannot create (403)
- [x] test_create_event_as_admin — Admin can create event
- [x] test_retrieve_event — Get single event detail
- [x] test_update_event_as_owner — Event organizer can update
- [x] test_update_event_as_non_owner — Different organizer cannot update (403)
- [x] test_update_event_as_admin — Admin can update any event
- [x] test_delete_event_as_owner — Organizer can delete own event
- [x] test_delete_event_as_non_owner — Non-owner cannot delete (403)
- [x] test_my_events — Filter events by current organizer
- [x] test_search_events — Search by title/category
- [x] test_filter_events_by_category — Filter by category
- [x] test_filter_events_by_date — Filter by event date range
- [x] test_order_events — Order by title/date
- [x] test_remaining_slots_set_on_create — remaining_slots = capacity on creation
- [x] test_event_time_validation — End time must be after start time
- [x] test_unauthenticated_user_cannot_access — 401 for unauthenticated

## Registration Tests (`registrations/tests.py`)
- [x] test_student_register_for_event — Student can register for an available event
- [x] test_organizer_cannot_register — Organizer gets 403
- [x] test_cannot_register_for_own_event — Event organizer cannot register for their own event
- [x] test_cannot_register_twice — Duplicate registration rejected
- [x] test_cannot_register_when_full — Registration rejected when slots are 0
- [x] test_list_registrations_as_student — Student sees own registrations only
- [x] test_list_registrations_as_organizer — Organizer sees registrations for their events
- [x] test_list_registrations_as_admin — Admin sees all registrations
- [x] test_cancel_registration — Cancel restores slot and sets CANCELLED status
- [x] test_cancel_already_cancelled — Cannot cancel already cancelled registration
- [x] test_mark_attended_as_organizer — Organizer can mark attendance for their event's registrations
- [x] test_mark_attended_as_admin — Admin can mark attendance
- [x] test_mark_attended_as_student — Student cannot mark attendance (403)
- [x] test_mark_attended_already_cancelled — Cannot mark attended for cancelled registration
- [x] test_slot_incremented_on_cancel — Verify remaining_slots increases on cancel
- [x] test_slot_decremented_on_register — Verify remaining_slots decreases on register

