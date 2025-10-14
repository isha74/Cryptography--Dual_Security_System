import pandas as pd
from pathlib import Path
from datetime import datetime


EXCEL_PATH = Path("instance/user_data.xlsx")


def ensure_excel_schema() -> None:
    """Ensure the Excel file exists with the expected schema."""
    if EXCEL_PATH.parent and not EXCEL_PATH.parent.exists():
        EXCEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not EXCEL_PATH.exists() or EXCEL_PATH.stat().st_size == 0:
        df = pd.DataFrame(columns=[
            "id", "username", "email", "password_hash", "created_at", "is_active"
        ])
        df.to_excel(EXCEL_PATH.as_posix(), index=False)


def load_users_df() -> pd.DataFrame:
    """Load users as a DataFrame; create schema if missing."""
    ensure_excel_schema()
    try:
        return pd.read_excel(EXCEL_PATH)
    except Exception:
        # If file is corrupted or empty, reset schema
        ensure_excel_schema()
        return pd.read_excel(EXCEL_PATH)


def save_users_df(df: pd.DataFrame) -> None:
    """Persist the given users DataFrame back to Excel."""
    ensure_excel_schema()
    df.to_excel(EXCEL_PATH.as_posix(), index=False)


def get_next_user_id(df: pd.DataFrame) -> int:
    if df.empty or "id" not in df or df["id"].isna().all():
        return 1
    return int(df["id"].max()) + 1


def get_user_by_username(username: str) -> dict | None:
    df = load_users_df()
    matches = df[df["username"].astype(str).str.lower() == str(username).lower()]
    if matches.empty:
        return None
    return matches.iloc[0].to_dict()


def get_user_by_email(email: str) -> dict | None:
    df = load_users_df()
    matches = df[df["email"].astype(str).str.lower() == str(email).lower()]
    if matches.empty:
        return None
    return matches.iloc[0].to_dict()


def get_user_by_id(user_id: int) -> dict | None:
    df = load_users_df()
    matches = df[df["id"] == int(user_id)]
    if matches.empty:
        return None
    return matches.iloc[0].to_dict()


def add_user(username: str, email: str, password_hash: str) -> dict:
    df = load_users_df()
    if not df[df["username"].astype(str).str.lower() == username.lower()].empty:
        raise ValueError("Username already exists")
    if not df[df["email"].astype(str).str.lower() == email.lower()].empty:
        raise ValueError("Email already registered")

    new_user = {
        "id": get_next_user_id(df),
        "username": username,
        "email": email,
        "password_hash": password_hash,
        "created_at": datetime.utcnow().isoformat(),
        "is_active": True,
    }
    df = pd.concat([df, pd.DataFrame([new_user])], ignore_index=True)
    save_users_df(df)
    return new_user


if __name__ == "__main__":
    # Ensure Excel schema exists when run directly
    ensure_excel_schema()
    print("✅ Excel user store ready at instance/user_data.xlsx")
