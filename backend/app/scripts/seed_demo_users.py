from app.db.session import get_session_factory
from app.services.demo_seed_service import DEMO_USERS, DemoSeedService


def main() -> None:
    session_factory = get_session_factory()
    with session_factory() as session:
        result = DemoSeedService().seed(session)

    print(
        "Seeded or refreshed "
        f"{result.users} demo users, "
        f"{result.employees} employees, "
        f"{result.review_cycles} review cycles, and "
        f"{result.evaluations} evaluations."
    )
    print("Available demo usernames:")
    for demo_user in DEMO_USERS:
        print(f"- {demo_user.username}")


if __name__ == "__main__":
    main()
