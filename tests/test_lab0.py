import pymysql
import pytest


@pytest.fixture
def connection():
    conn = pymysql.connect(
        host="127.0.0.1",
        user="root",
        password="root",
        autocommit=True
    )

    yield conn

    conn.close()
    
@pytest.fixture
def cursor(connection):
    cur = connection.cursor()

    yield cur

    cur.close()



def test_01_create_database(cursor):
    """
    Exercise 1

    Create a database named LibraryDB.
    """

    sql = """
    -- WRITE YOUR SQL HERE
    """

    cursor.execute(sql)

    cursor.execute("""
        SHOW DATABASES LIKE 'LibraryDB'
    """)

    assert cursor.fetchone() is not None


def test_02_create_members_table(connection):
    """
    Exercise 2

    Create the Members table with:

    - member_id primary key
    - first_name NOT NULL
    - last_name NOT NULL
    - age
    - city
    """

    sql = """
    -- WRITE YOUR SQL HERE
    """

    cur = connection.cursor()

    cur.execute("USE LibraryDB")
    cur.execute(sql)

    cur.execute("""
        SHOW COLUMNS
        FROM Members
    """)

    columns = {
        row[0]
        for row in cur.fetchall()
    }

    expected = {
        "member_id",
        "first_name",
        "last_name",
        "age",
        "city"
    }

    assert expected <= columns


def test_03_create_books_table(connection):
    """
    Exercise 3

    Create the Books table.

    Required columns:

    - book_id primary key
    - title
    - category
    """

    sql = """
    -- WRITE YOUR SQL HERE
    """

    cur = connection.cursor()

    cur.execute("USE LibraryDB")
    cur.execute(sql)

    cur.execute("""
        SHOW TABLES LIKE 'Books'
    """)

    assert cur.fetchone() is not None


def test_04_create_librarians_table(connection):
    """
    Exercise 4

    Create the Librarians table.

    Required columns:

    - librarian_id primary key
    - first_name
    - last_name
    - section
    """

    sql = """
    -- WRITE YOUR SQL HERE
    """

    cur = connection.cursor()

    cur.execute("USE LibraryDB")
    cur.execute(sql)

    cur.execute("""
        SHOW TABLES LIKE 'Librarians'
    """)

    assert cur.fetchone() is not None


def test_05_create_loans_table(connection):
    """
    Exercise 5

    Create the Loans table.

    Required columns:

    - loan_id primary key
    - member_id
    - book_id
    - loan_period

    Do NOT create foreign keys.
    """

    sql = """
    -- WRITE YOUR SQL HERE
    """

    cur = connection.cursor()

    cur.execute("USE LibraryDB")
    cur.execute(sql)

    cur.execute("""
        SHOW TABLES LIKE 'Loans'
    """)

    assert cur.fetchone() is not None


def test_06_insert_members(connection):
    """
    Exercise 6

    Insert three members into Members.
    """

    sql = """
    -- WRITE YOUR SQL HERE
    """

    cur = connection.cursor()

    cur.execute("USE LibraryDB")

    cur.execute(sql)

    cur.execute("""
        SELECT COUNT(*)
        FROM Members
    """)

    assert cur.fetchone()[0] == 3


def test_07_insert_books(connection):
    """
    Exercise 7

    Insert three books into Books.
    """

    sql = """
    -- WRITE YOUR SQL HERE
    """

    cur = connection.cursor()

    cur.execute("USE LibraryDB")

    cur.execute(sql)

    cur.execute("""
        SELECT COUNT(*)
        FROM Books
    """)

    assert cur.fetchone()[0] == 3


def test_08_insert_librarians(connection):
    """
    Exercise 8

    Insert three librarians.

    Each librarian should belong
    to a different section.
    """

    sql = """
    -- WRITE YOUR SQL HERE
    """

    cur = connection.cursor()

    cur.execute("USE LibraryDB")

    cur.execute(sql)

    cur.execute("""
        SELECT COUNT(*)
        FROM Librarians
    """)

    assert cur.fetchone()[0] == 3


def test_09_insert_loans(connection):
    """
    Exercise 9

    Insert three loans.

    Every loan must contain a loan_period.
    """

    sql = """
    -- WRITE YOUR SQL HERE
    """

    cur = connection.cursor()

    cur.execute("USE LibraryDB")

    cur.execute(sql)

    cur.execute("""
        SELECT COUNT(*)
        FROM Loans
    """)

    assert cur.fetchone()[0] == 3

def test_10_list_all_members(connection):
    """
    Query 1

    List all members.
    """

    cur = connection.cursor()

    cur.execute("USE LibraryDB")

    sql = """
    -- WRITE YOUR SQL HERE
    """

    cur.execute(sql)

    rows = cur.fetchall()

    assert len(rows) == 3


def test_11_list_book_titles(connection):
    """
    Query 2

    List only the book titles.
    """

    cur = connection.cursor()

    cur.execute("USE LibraryDB")

    sql = """
    -- WRITE YOUR SQL HERE
    """

    cur.execute(sql)

    rows = cur.fetchall()

    assert rows == (
        ("Introduction to Databases",),
        ("Discrete Mathematics",),
        ("Operating Systems Concepts",),
    )


def test_12_members_older_than_20(connection):
    """
    Query 3

    Find all members older than 20.
    """

    cur = connection.cursor()

    cur.execute("USE LibraryDB")

    sql = """
    -- WRITE YOUR SQL HERE
    """

    cur.execute(sql)

    rows = cur.fetchall()

    assert len(rows) == 2


def test_13_librarians_digital_resources(connection):
    """
    Query 4

    Find all librarians in the
    Digital Resources section.
    """

    cur = connection.cursor()

    cur.execute("USE LibraryDB")

    sql = """
    -- WRITE YOUR SQL HERE
    """

    cur.execute(sql)

    rows = cur.fetchall()

    assert len(rows) == 1


def test_14_january_loans(connection):
    """
    Query 5

    List all loans that took place
    in January 2026.
    """

    cur = connection.cursor()

    cur.execute("USE LibraryDB")

    sql = """
    -- WRITE YOUR SQL HERE
    """

    cur.execute(sql)

    rows = cur.fetchall()

    assert len(rows) == 2


def test_15_distinct_cities(connection):
    """
    Query 6

    Show distinct cities.
    """

    cur = connection.cursor()

    cur.execute("USE LibraryDB")

    sql = """
    -- WRITE YOUR SQL HERE
    """

    cur.execute(sql)

    rows = {
        row[0]
        for row in cur.fetchall()
    }

    assert rows == {
        "Casablanca",
        "Rabat",
        "Marrakech"
    }


def test_16_member_count(connection):
    """
    Query 7

    Count members.
    """

    cur = connection.cursor()

    cur.execute("USE LibraryDB")

    sql = """
    -- WRITE YOUR SQL HERE
    """

    cur.execute(sql)

    result = cur.fetchone()[0]

    assert result == 3


def test_17_average_age(connection):
    """
    Query 8

    Find average age.
    """

    cur = connection.cursor()

    cur.execute("USE LibraryDB")

    sql = """
    -- WRITE YOUR SQL HERE
    """

    cur.execute(sql)

    result = float(cur.fetchone()[0])

    assert round(result, 2) == 21.33


def test_18_names_starting_with_s(connection):
    """
    Query 9

    Find members whose first name
    starts with S.
    """

    cur = connection.cursor()

    cur.execute("USE LibraryDB")

    sql = """
    -- WRITE YOUR SQL HERE
    """

    cur.execute(sql)

    rows = cur.fetchall()

    assert len(rows) == 0


def test_19_age_between_20_and_22(connection):
    """
    Query 10

    Find members aged
    between 20 and 22 inclusive.
    """

    cur = connection.cursor()

    cur.execute("USE LibraryDB")

    sql = """
    -- WRITE YOUR SQL HERE
    """

    cur.execute(sql)

    rows = cur.fetchall()

    assert len(rows) == 2


def test_20_sorted_members(connection):
    """
    Query 11

    Sort by city ascending,
    then age descending.
    """

    cur = connection.cursor()

    cur.execute("USE LibraryDB")

    sql = """
    -- WRITE YOUR SQL HERE
    """

    cur.execute(sql)

    rows = cur.fetchall()

    cities = [row[4] for row in rows]

    assert cities == sorted(cities)


def test_21_first_two_members(connection):
    """
    Query 12

    Retrieve only the first
    two members.
    """

    cur = connection.cursor()

    cur.execute("USE LibraryDB")

    sql = """
    -- WRITE YOUR SQL HERE
    """

    cur.execute(sql)

    rows = cur.fetchall()

    assert len(rows) == 2


def test_22_loans_grouped_by_period(connection):
    """
    Query 13

    Count loans per loan period
    using GROUP BY.
    """

    cur = connection.cursor()

    cur.execute("USE LibraryDB")

    sql = """
    -- WRITE YOUR SQL HERE
    """

    cur.execute(sql)

    rows = cur.fetchall()

    assert len(rows) == 2

    periods = {
        row[0]
        for row in rows
    }

    assert periods == {
        "January 2026",
        "February 2026"
    }