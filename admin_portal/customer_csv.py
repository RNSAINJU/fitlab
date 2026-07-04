import csv
import io
from datetime import datetime

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime

User = get_user_model()

CSV_HEADERS = [
    "member_id",
    "name",
    "gender",
    "date_of_birth",
    "phone",
    "email",
    "address",
    "joined_date",
    "created_at",
]

HEADER_ALIASES = {
    "member_id": "member_id",
    "member id": "member_id",
    "memberid": "member_id",
    "name": "name",
    "full name": "name",
    "gender": "gender",
    "sex": "gender",
    "date_of_birth": "date_of_birth",
    "dateofbirth": "date_of_birth",
    "date of birth": "date_of_birth",
    "dob": "date_of_birth",
    "phone": "phone",
    "phone number": "phone",
    "mobile": "phone",
    "mobile number": "phone",
    "email": "email",
    "email address": "email",
    "address": "address",
    "joined_date": "joined_date",
    "joined date": "joined_date",
    "date joined": "joined_date",
    "created_at": "created_at",
    "created at": "created_at",
    "created at timestamp": "created_at",
    "created_at timestamp": "created_at",
}

GENDER_MAP = {
    "male": User.Gender.MALE,
    "m": User.Gender.MALE,
    "female": User.Gender.FEMALE,
    "f": User.Gender.FEMALE,
    "other": User.Gender.OTHER,
    "prefer not to say": User.Gender.PREFER_NOT,
    "prefer_not": User.Gender.PREFER_NOT,
}


def _normalize_header(value):
    key = (value or "").strip().lower().replace("_", " ")
    key = " ".join(key.split())
    return HEADER_ALIASES.get(key, key.replace(" ", "_"))


def _parse_gender(value):
    raw = (value or "").strip().lower()
    if not raw:
        return ""
    if raw in GENDER_MAP:
        return GENDER_MAP[raw]
    for choice, label in User.Gender.choices:
        if raw == label.lower():
            return choice
    raise ValueError(f"Unknown gender: {value}")


def _parse_date(value):
    raw = (value or "").strip()
    if not raw:
        return None
    parsed = parse_date(raw)
    if parsed:
        return parsed
    for fmt in ("%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y", "%m-%d-%Y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Invalid date: {value}")


def _parse_datetime(value):
    raw = (value or "").strip()
    if not raw:
        return None
    parsed = parse_datetime(raw)
    if parsed:
        if timezone.is_naive(parsed):
            return timezone.make_aware(parsed, timezone.get_current_timezone())
        return parsed
    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%m/%d/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            dt = datetime.strptime(raw, fmt)
            return timezone.make_aware(dt, timezone.get_current_timezone())
        except ValueError:
            continue
    date_only = _parse_date(raw)
    if date_only:
        return timezone.make_aware(
            datetime.combine(date_only, datetime.min.time()),
            timezone.get_current_timezone(),
        )
    raise ValueError(f"Invalid timestamp: {value}")


def _split_name(name):
    parts = (name or "").strip().split(None, 1)
    if not parts:
        return "", ""
    return parts[0], parts[1] if len(parts) > 1 else ""


def _row_to_dict(reader_row, field_map):
    data = {}
    for src, dest in field_map.items():
        if src in reader_row:
            data[dest] = (reader_row.get(src) or "").strip()
    return data


def customer_to_row(user):
    joined = user.date_joined
    if joined and timezone.is_naive(joined):
        joined = timezone.make_aware(joined, timezone.get_current_timezone())
    return {
        "member_id": user.member_id or "",
        "name": user.display_name,
        "gender": user.get_gender_display() if user.gender else "",
        "date_of_birth": user.date_of_birth.isoformat() if user.date_of_birth else "",
        "phone": user.phone,
        "email": user.email,
        "address": user.address,
        "joined_date": joined.strftime("%Y-%m-%d") if joined else "",
        "created_at": joined.isoformat() if joined else "",
    }


def export_customers_csv(stream):
    writer = csv.DictWriter(stream, fieldnames=CSV_HEADERS)
    writer.writeheader()
    customers = User.objects.filter(is_staff=False).order_by("member_id", "email")
    for user in customers:
        writer.writerow(customer_to_row(user))


def import_customers_csv(uploaded_file):
    created = 0
    updated = 0
    errors = []

    try:
        raw = uploaded_file.read().decode("utf-8-sig")
    except UnicodeDecodeError:
        return 0, 0, ["CSV file must be UTF-8 encoded."]

    reader = csv.DictReader(io.StringIO(raw))
    if not reader.fieldnames:
        return 0, 0, ["CSV file is missing a header row."]

    field_map = {}
    for header in reader.fieldnames:
        normalized = _normalize_header(header)
        if normalized in CSV_HEADERS:
            field_map[header] = normalized

    if "email" not in field_map.values() and "member_id" not in field_map.values():
        return 0, 0, ["CSV must include at least an email or member_id column."]

    for line_no, row in enumerate(reader, start=2):
        if not any((value or "").strip() for value in row.values()):
            continue

        data = _row_to_dict(row, field_map)
        try:
            member_id = data.get("member_id") or None
            email = data.get("email", "").lower()
            name = data.get("name", "")

            user = None
            if member_id:
                user = User.objects.filter(member_id=member_id, is_staff=False).first()
            if user is None and email:
                user = User.objects.filter(email__iexact=email, is_staff=False).first()

            is_new = user is None
            if is_new:
                if not email:
                    raise ValueError("Email is required for new members.")
                user = User(email=email, username=email)
                user.set_unusable_password()
                user.approval_status = User.ApprovalStatus.APPROVED

            if name:
                first_name, last_name = _split_name(name)
                user.first_name = first_name
                user.last_name = last_name

            if email:
                user.email = email
                if not user.username or user.username == user.email:
                    user.username = email

            if member_id:
                user.member_id = member_id

            if "phone" in data:
                user.phone = data.get("phone", "")

            if "address" in data:
                user.address = data.get("address", "")

            if "gender" in data:
                user.gender = _parse_gender(data.get("gender", ""))

            if "date_of_birth" in data and data.get("date_of_birth"):
                user.date_of_birth = _parse_date(data.get("date_of_birth"))

            joined_dt = None
            if data.get("created_at"):
                joined_dt = _parse_datetime(data.get("created_at"))
            elif data.get("joined_date"):
                joined_dt = _parse_datetime(data.get("joined_date"))

            if joined_dt:
                user.date_joined = joined_dt

            user.save()

            if is_new:
                created += 1
            else:
                updated += 1
        except Exception as exc:
            label = data.get("email") or data.get("member_id") or f"row {line_no}"
            errors.append(f"Line {line_no} ({label}): {exc}")

    return created, updated, errors
