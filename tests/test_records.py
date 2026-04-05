import uuid

import pytest

from apps.records.constants import RecordStatus, RecordType
from apps.records.models import FinancialRecord
from tests.factories import FinancialRecordFactory


RECORDS_URL = "/api/records/"


def record_detail_url(pk):
	return f"/api/records/{pk}/"


@pytest.mark.django_db
class TestRecordCreate:
	def test_admin_can_create_record_returns_201_when_payload_valid(self, admin_client):
		payload = {
			"amount": "5000.00",
			"type": RecordType.INCOME,
			"category": "Consulting",
			"date": "2024-04-01",
			"currency": "INR",
			"status": RecordStatus.PENDING,
		}
		response = admin_client.post(RECORDS_URL, payload, format="json")

		assert response.status_code == 201
		assert response.data["status"] is True
		assert response.data["data"]["category"] == "Consulting"
		assert "reference_number" in response.data["data"]

	def test_reference_number_auto_generated_on_create_when_record_created(self, admin_client):
		payload = {
			"amount": "1000.00",
			"type": RecordType.EXPENSE,
			"category": "Office",
			"date": "2024-04-01",
		}
		response = admin_client.post(RECORDS_URL, payload, format="json")

		assert response.status_code == 201
		assert response.data["status"] is True
		assert response.data["data"]["reference_number"].startswith("TXN-")

	def test_viewer_cannot_create_record_returns_403_when_role_is_viewer(self, viewer_client):
		payload = {
			"amount": "1000.00",
			"type": RecordType.INCOME,
			"category": "Test",
			"date": "2024-04-01",
		}
		response = viewer_client.post(RECORDS_URL, payload, format="json")

		assert response.status_code == 403
		assert response.data["status"] == "error"

	def test_analyst_cannot_create_record_returns_403_when_role_is_analyst(self, analyst_client):
		payload = {
			"amount": "1000.00",
			"type": RecordType.INCOME,
			"category": "Test",
			"date": "2024-04-01",
		}
		response = analyst_client.post(RECORDS_URL, payload, format="json")

		assert response.status_code == 403
		assert response.data["status"] == "error"

	def test_create_record_zero_amount_returns_400_when_amount_is_zero(self, admin_client):
		payload = {
			"amount": "0.00",
			"type": RecordType.INCOME,
			"category": "Test",
			"date": "2024-04-01",
		}
		response = admin_client.post(RECORDS_URL, payload, format="json")

		assert response.status_code == 400
		assert response.data["status"] == "error"

	def test_create_record_negative_amount_returns_400_when_amount_is_negative(self, admin_client):
		payload = {
			"amount": "-500.00",
			"type": RecordType.INCOME,
			"category": "Test",
			"date": "2024-04-01",
		}
		response = admin_client.post(RECORDS_URL, payload, format="json")

		assert response.status_code == 400
		assert response.data["status"] == "error"

	def test_create_record_missing_required_field_returns_400_when_date_missing(self, admin_client):
		payload = {
			"amount": "1000.00",
			"type": RecordType.INCOME,
			"category": "Test",
		}
		response = admin_client.post(RECORDS_URL, payload, format="json")

		assert response.status_code == 400
		assert response.data["status"] == "error"


@pytest.mark.django_db
class TestRecordRead:
	def test_viewer_can_list_records_returns_200_when_authenticated(self, viewer_client, pending_record):
		response = viewer_client.get(RECORDS_URL)

		assert response.status_code == 200
		assert response.data["status"] is True

	def test_analyst_can_list_records_returns_200_when_authenticated(self, analyst_client, pending_record):
		response = analyst_client.get(RECORDS_URL)

		assert response.status_code == 200
		assert response.data["status"] is True

	def test_list_records_excludes_soft_deleted_when_querying_default_manager(self, admin_client, admin_user):
		active = FinancialRecordFactory(created_by=admin_user)
		deleted = FinancialRecordFactory(created_by=admin_user, is_deleted=True)
		response = admin_client.get(RECORDS_URL)
		ids = [row["id"] for row in response.data["data"]["results"]]

		assert response.status_code == 200
		assert response.data["status"] is True
		assert str(active.id) in ids
		assert str(deleted.id) not in ids

	def test_filter_by_type_returns_correct_records_when_type_query_applied(self, admin_client, admin_user):
		FinancialRecordFactory(created_by=admin_user, type=RecordType.INCOME)
		FinancialRecordFactory(created_by=admin_user, type=RecordType.EXPENSE)
		response = admin_client.get(f"{RECORDS_URL}?type={RecordType.INCOME}")
		results = response.data["data"]["results"]

		assert response.status_code == 200
		assert response.data["status"] is True
		assert all(item["type"] == RecordType.INCOME for item in results)

	def test_unauthenticated_list_returns_401_when_token_missing(self, api_client):
		response = api_client.get(RECORDS_URL)

		assert response.status_code == 401
		assert response.data["status"] == "error"


@pytest.mark.django_db
class TestRecordUpdate:
	def test_admin_can_update_pending_record_returns_200_when_status_pending(self, admin_client, pending_record):
		response = admin_client.patch(
			record_detail_url(pending_record.id),
			{"category": "Updated Category"},
			format="json",
		)

		assert response.status_code == 200
		assert response.data["status"] is True
		assert response.data["data"]["category"] == "Updated Category"

	def test_cannot_update_completed_record_returns_400_when_status_completed(self, admin_client, completed_record):
		response = admin_client.patch(
			record_detail_url(completed_record.id),
			{"category": "New Category"},
			format="json",
		)

		assert response.status_code == 400
		assert response.data["status"] == "error"

	def test_cannot_update_cancelled_record_returns_400_when_status_cancelled(self, admin_client, admin_user):
		record = FinancialRecordFactory(created_by=admin_user, status=RecordStatus.CANCELLED)
		response = admin_client.patch(
			record_detail_url(record.id),
			{"category": "New Category"},
			format="json",
		)

		assert response.status_code == 400
		assert response.data["status"] == "error"

	def test_viewer_cannot_update_record_returns_403_when_role_is_viewer(self, viewer_client, pending_record):
		response = viewer_client.patch(
			record_detail_url(pending_record.id),
			{"category": "Hacked"},
			format="json",
		)

		assert response.status_code == 403
		assert response.data["status"] == "error"

	def test_update_record_type_ignored_when_type_field_not_updatable(self, admin_client, pending_record):
		original_type = pending_record.type
		admin_client.patch(record_detail_url(pending_record.id), {"type": RecordType.EXPENSE}, format="json")
		pending_record.refresh_from_db()

		assert pending_record.type == original_type


@pytest.mark.django_db
class TestRecordDelete:
	def test_admin_soft_deletes_record_returns_204_when_record_exists(self, admin_client, pending_record):
		response = admin_client.delete(record_detail_url(pending_record.id))
		pending_record.refresh_from_db()
		record = FinancialRecord.all_objects.get(id=pending_record.id)

		assert response.status_code == 204
		assert record.is_deleted is True
		assert record.deleted_at is not None

	def test_soft_deleted_record_not_in_list_when_deleted_before_list(self, admin_client, pending_record):
		admin_client.delete(record_detail_url(pending_record.id))
		list_response = admin_client.get(RECORDS_URL)
		ids = [item["id"] for item in list_response.data["data"]["results"]]

		assert list_response.status_code == 200
		assert list_response.data["status"] is True
		assert str(pending_record.id) not in ids

	def test_viewer_cannot_delete_record_returns_403_when_role_is_viewer(self, viewer_client, pending_record):
		response = viewer_client.delete(record_detail_url(pending_record.id))

		assert response.status_code == 403
		assert response.data["status"] == "error"

	def test_delete_nonexistent_record_returns_404_when_record_missing(self, admin_client):
		response = admin_client.delete(record_detail_url(uuid.uuid4()))

		assert response.status_code == 404
		assert response.data["status"] == "error"
