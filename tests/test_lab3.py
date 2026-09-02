import os
import pymysql
import pytest


# CONFIG
DB_NAME = "RLMS_LAB3"
SHADOW_DB_NAME = "RLMS_LAB3_SHADOW"
HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA_FILE = os.path.join(HERE, "schema.sql")
SEED_FILE = os.path.join(HERE, "seed.sql")
SHADOW_SEED_FILE = os.path.join(HERE, "seed_shadow.sql")



@pytest.fixture(scope="session")
def admin_connection():
    """Used only for one-time setup (creating/dropping/seeding databases)."""
    conn = pymysql.connect(
        host="127.0.0.1",
        user="root",
        password="root",
        autocommit=True,
    )
    yield conn
    conn.close()


@pytest.fixture(scope="session")
def public_connection():
    conn = pymysql.connect(
        host="127.0.0.1",
        user="root",
        password="root",
        database=DB_NAME,
        autocommit=True,
    )
    yield conn
    conn.close()


@pytest.fixture(scope="session")
def shadow_connection():
    conn = pymysql.connect(
        host="127.0.0.1",
        user="root",
        password="root",
        database=SHADOW_DB_NAME,
        autocommit=True,
    )
    yield conn
    conn.close()


def _load_sql_file_into_db(cur, path, required_for_msg):
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Required file not found: {path}\n{required_for_msg}"
        )
    with open(path, "r", encoding="utf-8") as f:
        sql_text = f.read()

    clean_lines = []
    for line in sql_text.split("\n"):
        if "--" in line:
            line = line.split("--")[0]
        clean_lines.append(line)
    sql_text = "\n".join(clean_lines)

    for statement in sql_text.split(";"):
        statement = statement.strip()
        if not statement:
            continue
        if statement.upper().startswith("USE "):
            continue
        cur.execute(statement)


@pytest.fixture(scope="session", autouse=True)
def setup_database(admin_connection):
    cur = admin_connection.cursor()

    for db_name, seed_file in ((DB_NAME, SEED_FILE), (SHADOW_DB_NAME, SHADOW_SEED_FILE)):
        cur.execute(f"DROP DATABASE IF EXISTS {db_name}")
        cur.execute(f"CREATE DATABASE {db_name}")
        cur.execute(f"USE {db_name}")

        _load_sql_file_into_db(
            cur, SCHEMA_FILE,
            "Lab 3 grading requires schema.sql to sit next to test_lab3.py.",
        )
        _load_sql_file_into_db(
            cur, seed_file,
            "Lab 3 grading requires seed.sql and seed_shadow.sql to sit "
            "next to test_lab3.py.",
        )

    cur.close()
    yield


@pytest.fixture
def cursor(public_connection, setup_database):
    cur = public_connection.cursor()
    yield cur
    cur.close()


@pytest.fixture
def shadow_cursor(shadow_connection, setup_database):
    cur = shadow_connection.cursor()
    yield cur
    cur.close()


# COMPARISON HELPER
def normalize(rows):
    """Order-insensitive comparison: sorted tuple multiset."""
    return sorted(tuple(row) for row in rows)


def assert_matches_expected(cursor, shadow_cursor, sql, expected, shadow_expected, query_label):
    if expected is None or shadow_expected is None:
        pytest.skip(
            f"{query_label}: no expected-results entry filled in yet for "
            f"one or both datasets -- skipping rather than risking a false pass."
        )

    cursor.execute(sql)
    actual_rows = normalize(cursor.fetchall())
    expected_rows = normalize(expected)

    shadow_cursor.execute(sql)
    shadow_actual_rows = normalize(shadow_cursor.fetchall())
    shadow_expected_rows = normalize(shadow_expected)

    public_ok = actual_rows == expected_rows
    shadow_ok = shadow_actual_rows == shadow_expected_rows

    if public_ok and shadow_ok:
        return

    details = []
    if not public_ok:
        details.append(
            f"public dataset result mismatch:\n"
            f"    Expected ({len(expected_rows)} row(s)): {expected_rows}\n"
            f"    Got      ({len(actual_rows)} row(s)): {actual_rows}"
        )
    if not shadow_ok:
        details.append(
            f"hidden verification dataset result mismatch: "
            f"expected {len(shadow_expected_rows)} row(s), "
            f"got {len(shadow_actual_rows)} row(s) "
        )
        if public_ok:
            details.append(
                "    (this query matched the public dataset but NOT the hidden "
            )

    pytest.fail(f"{query_label} result mismatch:\n  " + "\n  ".join(details))


try:
    from lab3_answers import EXPECTED_RESULTS
except ImportError as exc:
    raise ImportError(
        "lab3_answers.py not found.3"
    ) from exc

try:
    from lab3_answers_shadow import EXPECTED_RESULTS as SHADOW_EXPECTED_RESULTS
except ImportError as exc:
    raise ImportError(
        "lab3_answers_shadow.py not found."
    ) from exc


# 
def test_01_research_users_with_reservation(cursor, shadow_cursor):
    """
    Query 1

    Find the names of research users who have made at least one reservation.
    """
    sql = """
    SELECT DISTINCT p.FullName
    FROM Person p
    JOIN ResearchUser ru ON p.PersonID = ru.PersonID
    JOIN Reservation r ON r.PersonID = p.PersonID
    """
    assert_matches_expected(cursor, shadow_cursor, sql, EXPECTED_RESULTS[1], SHADOW_EXPECTED_RESULTS[1], "Q1")


def test_02_users_attached_or_leading_project(cursor, shadow_cursor):
    """
    Query 2

    Find the IDs of research users who are either assigned to a laboratory
    or are leading at least one research project.
    """
    sql = """
    SELECT DISTINCT ru.PersonID
    FROM ResearchUser ru
    WHERE ru.PersonID IN (SELECT PersonID FROM AttachedTo)
       OR ru.PersonID IN (
           SELECT PersonID FROM ProjectParticipation WHERE ProjectRole = 'PI'
       )
    """
    assert_matches_expected(cursor, shadow_cursor, sql, EXPECTED_RESULTS[2], SHADOW_EXPECTED_RESULTS[2], "Q2")


def test_03_labs_research_center_a_or_microscope(cursor, shadow_cursor):
    """
    Query 3

    Find the IDs of laboratories located in the building 'Research Center A'
    or having at least one equipment item of category 'Microscope'.
    """
    sql = """
    SELECT DISTINCT l.LabID
    FROM Laboratory l
    WHERE l.Building = 'Research Center A'
       OR l.LabID IN (
           SELECT eu.LabID
           FROM EquipmentUnit eu
           JOIN EquipmentModel em ON eu.ModelID = em.ModelID
           WHERE em.Category = 'Microscope'
       )
    """
    assert_matches_expected(cursor, shadow_cursor, sql, EXPECTED_RESULTS[3], SHADOW_EXPECTED_RESULTS[3], "Q3")


def test_04_labs_with_microscope_and_centrifuge(cursor, shadow_cursor):
    """
    Query 4

    Find the IDs of laboratories that contain both 'Microscope' and
    'Centrifuge' equipment.
    """
    sql = """
    SELECT eu.LabID
    FROM EquipmentUnit eu
    JOIN EquipmentModel em ON eu.ModelID = em.ModelID
    WHERE em.Category IN ('Microscope', 'Centrifuge')
    GROUP BY eu.LabID
    HAVING COUNT(DISTINCT em.Category) = 2
    """
    assert_matches_expected(cursor, shadow_cursor, sql, EXPECTED_RESULTS[4], SHADOW_EXPECTED_RESULTS[4], "Q4")


def test_05_supervisors_of_every_north_wing_lab(cursor, shadow_cursor):
    """
    Query 5

    Find the research users who supervise every laboratory located in
    building 'North Wing'.
    """
    sql = """
    SELECT ru.PersonID
    FROM ResearchUser ru
    WHERE NOT EXISTS (
        SELECT 1 FROM Laboratory l
        WHERE l.Building = 'North Wing'
          AND (l.SupervisorID IS NULL OR l.SupervisorID <> ru.PersonID)
    )
    """
    assert_matches_expected(cursor, shadow_cursor, sql, EXPECTED_RESULTS[5], SHADOW_EXPECTED_RESULTS[5], "Q5")


def test_06_participants_in_every_lab2_project(cursor, shadow_cursor):
    """
    Query 6

    Find the research users who participate in every research project
    supervised by laboratory with LabID = 2.
    """
    sql = """
    SELECT ru.PersonID
    FROM ResearchUser ru
    WHERE NOT EXISTS (
        SELECT 1 FROM ProjectParticipation pp_lead
        WHERE pp_lead.PersonID = (SELECT SupervisorID FROM Laboratory WHERE LabID = 'L0002')
          AND pp_lead.ProjectRole = 'PI'
          AND NOT EXISTS (
              SELECT 1 FROM ProjectParticipation pp_self
              WHERE pp_self.PersonID = ru.PersonID
                AND pp_self.ProjectCode = pp_lead.ProjectCode
          )
    )
    """
    assert_matches_expected(cursor, shadow_cursor, sql, EXPECTED_RESULTS[6], SHADOW_EXPECTED_RESULTS[6], "Q6")


def test_07_pairs_more_reservations(cursor, shadow_cursor):
    """
    Query 7

    Find pairs of research users (r1, r2) such that r1 has made more
    reservations than r2.
    """
    sql = """
    SELECT a.PersonID, b.PersonID
    FROM (SELECT PersonID, COUNT(*) AS c FROM Reservation GROUP BY PersonID) a,
         (SELECT PersonID, COUNT(*) AS c FROM Reservation GROUP BY PersonID) b
    WHERE a.c > b.c
    """
    assert_matches_expected(cursor, shadow_cursor, sql, EXPECTED_RESULTS[7], SHADOW_EXPECTED_RESULTS[7], "Q7")


def test_08_users_reserved_two_different_labs(cursor, shadow_cursor):
    """
    Query 8

    Find the IDs of research users who have reserved equipment units
    belonging to at least two different laboratories.
    """
    sql = """
    SELECT r.PersonID
    FROM Reservation r
    JOIN EquipmentUnit eu ON r.SerialNumber = eu.SerialNumber
    GROUP BY r.PersonID
    HAVING COUNT(DISTINCT eu.LabID) >= 2
    """
    assert_matches_expected(cursor, shadow_cursor, sql, EXPECTED_RESULTS[8], SHADOW_EXPECTED_RESULTS[8], "Q8")


def test_09_september_2026_biolab_a_reservations(cursor, shadow_cursor):
    """
    Query 9

    Find the reservation IDs of reservations made in September 2026 for
    equipment units located in the laboratory named 'BioLab-A'.
    """
    sql = """
    SELECT r.ReservationID
    FROM Reservation r
    JOIN EquipmentUnit eu ON r.SerialNumber = eu.SerialNumber
    JOIN Laboratory l ON eu.LabID = l.LabID
    WHERE l.Name = 'BioLab-A'
      AND r.PlannedStartTime >= '2026-09-01 00:00:00'
      AND r.PlannedStartTime <  '2026-10-01 00:00:00'
    """
    assert_matches_expected(cursor, shadow_cursor, sql, EXPECTED_RESULTS[9], SHADOW_EXPECTED_RESULTS[9], "Q9")


def test_10_users_leading_more_than_one_project(cursor, shadow_cursor):
    """
    Query 10

    Find the IDs of research users who lead more than one research project.
    """
    sql = """
    SELECT PersonID
    FROM ProjectParticipation
    WHERE ProjectRole = 'PI'
    GROUP BY PersonID
    HAVING COUNT(*) > 1
    """
    assert_matches_expected(cursor, shadow_cursor, sql, EXPECTED_RESULTS[10], SHADOW_EXPECTED_RESULTS[10], "Q10")


def test_11_users_approved_in_multiple_labs(cursor, shadow_cursor):
    """
    Query 11

    List the IDs of research users who have approved reservations in more
    than one laboratory.
    """
    sql = """
    SELECT r.ApprovedBy
    FROM Reservation r
    JOIN EquipmentUnit eu ON r.SerialNumber = eu.SerialNumber
    WHERE r.ApprovedBy IS NOT NULL
    GROUP BY r.ApprovedBy
    HAVING COUNT(DISTINCT eu.LabID) > 1
    """
    assert_matches_expected(cursor, shadow_cursor, sql, EXPECTED_RESULTS[11], SHADOW_EXPECTED_RESULTS[11], "Q11")


def test_12_users_no_reservation_nov_6_2026(cursor, shadow_cursor):
    """
    Query 12

    Find the IDs of research users who have no reservation on
    November 6, 2026.
    """
    sql = """
    SELECT ru.PersonID
    FROM ResearchUser ru
    WHERE ru.PersonID NOT IN (
        SELECT PersonID FROM Reservation
        WHERE PlannedStartTime >= '2026-11-06 00:00:00'
          AND PlannedStartTime <  '2026-11-07 00:00:00'
    )
    """
    assert_matches_expected(cursor, shadow_cursor, sql, EXPECTED_RESULTS[12], SHADOW_EXPECTED_RESULTS[12], "Q12")


def test_13_labs_below_average_equipment_count(cursor, shadow_cursor):
    """
    Query 13

    Find laboratories whose number of equipment units is below the average
    number of equipment units per laboratory.
    """
    sql = """
    SELECT l.LabID
    FROM Laboratory l
    LEFT JOIN EquipmentUnit eu ON l.LabID = eu.LabID
    GROUP BY l.LabID
    HAVING COUNT(eu.SerialNumber) < (
        SELECT AVG(cnt) FROM (
            SELECT COUNT(*) AS cnt FROM EquipmentUnit GROUP BY LabID
        ) t
    )
    """
    assert_matches_expected(cursor, shadow_cursor, sql, EXPECTED_RESULTS[13], SHADOW_EXPECTED_RESULTS[13], "Q13")


def test_14_top_approver_per_lab(cursor, shadow_cursor):
    """
    Query 14

    For each laboratory, return the research user who has made the greatest
    number of approved reservations in that laboratory.
    """
    sql = """
    SELECT eu.LabID, r.PersonID
    FROM Reservation r
    JOIN EquipmentUnit eu ON r.SerialNumber = eu.SerialNumber
    WHERE r.Status = 'Approved'
    GROUP BY eu.LabID, r.PersonID
    HAVING COUNT(*) = (
        SELECT MAX(c) FROM (
            SELECT COUNT(*) AS c
            FROM Reservation r2
            JOIN EquipmentUnit eu2 ON r2.SerialNumber = eu2.SerialNumber
            WHERE r2.Status = 'Approved' AND eu2.LabID = eu.LabID
            GROUP BY r2.PersonID
        ) sub
    )
    """
    assert_matches_expected(cursor, shadow_cursor, sql, EXPECTED_RESULTS[14], SHADOW_EXPECTED_RESULTS[14], "Q14")


def test_15_users_three_plus_reservations_2025(cursor, shadow_cursor):
    """
    Query 15

    List the research users who made at least 3 reservations during the
    year 2025.
    """
    sql = """
    SELECT PersonID
    FROM Reservation
    WHERE PlannedStartTime >= '2025-01-01 00:00:00'
      AND PlannedStartTime <  '2026-01-01 00:00:00'
    GROUP BY PersonID
    HAVING COUNT(*) >= 3
    """
    assert_matches_expected(cursor, shadow_cursor, sql, EXPECTED_RESULTS[15], SHADOW_EXPECTED_RESULTS[15], "Q15")