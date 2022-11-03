# -*- coding: utf-8 -*-
"""Initialiser model

Contains a model that initialises the database. For use when first creating a database.
"""

import logging
from datetime import date
from pathlib import Path

from client.db import Database


class DatabaseInitialiser(Database):
    """Initialise a database."""

    def __init__(
        self, connection_string: str, populate_with_fake_data: bool = False
    ) -> None:
        """Initialise self then populate database."""
        super().__init__(connection_string)
        if populate_with_fake_data:
            # Warning: this deletes all data that already exists in tables!
            self.populate_with_fake_data()

    def init_db(self) -> None:
        """Create database tables."""

        logging.info("Creating database tables")
        init_instructions: Path = Path("initialise.sql")
        with open(init_instructions, "r") as sql_file:
            self.exec(sql_file.read())

    def populate_with_fake_data(self) -> None:
        """Populate the tables with fake data. This should only be used in development."""

        # Fake instruments
        self.exec("delete from instrument;")
        self.exec(
            "insert into instrument (name, status) values (%s, %s)",
            ("Nikon", "Utterly destroyed"),
        )
        self.exec(
            "insert into instrument (name, status) values (%s, %s)",
            ("Zeiss", "Working fine"),
        )
        self.exec(
            "insert into instrument (name, status) values (%s, %s)",
            ("Rapiscan", "Amin spilt coffee on it"),
        )
        # Fake samples
        self.exec("delete from sample;")
        self.exec(
            "insert into sample (name, size, material, confidentiality) values (%s, %s, %s, %s);",
            ("Mug", 15, "Ceramic", False),
        )
        self.exec(
            "insert into sample (name, size, material, confidentiality) values (%s, %s, %s, %s);",
            ("Bucket (no head)", 50, "Steel", True),
        )
        self.exec(
            "insert into sample (name, size, material, confidentiality) values (%s, %s, %s, %s);",
            ("Deadpool", 25, "Paper", False),
        )
        self.exec(
            "insert into sample (name, size, material, confidentiality) values (%s, %s, %s, %s);",
            ("Pocket watch", 5, "Gold", False),
        )
        # Fake users
        self.exec('delete from "user";')
        self.exec(
            'insert into "user" (first_name, last_name, email_address) values (%s, %s, %s);',
            ("Amin", "Garbout", "amin.garbout@manchester.ac.uk"),
        )
        self.exec(
            'insert into "user" (first_name, last_name, email_address) values (%s, %s, %s);',
            ("Elizabeth", "Evans", "elizabeth.evans-5@manchester.ac.uk"),
        )
        self.exec(
            'insert into "user" (first_name, last_name, email_address) values (%s, %s, %s);',
            ("Tristan", "Lowe", "Tristan.Lowe@manchester.ac.uk"),
        )
        # Fake projects
        self.exec("delete from project")
        self.exec(
            "insert into project (title, project_type, summary, keyword, start_date, end_date, directory_path) values (%s, %s, %s, %s, %s, %s, %s);",
            (
                "The caffeine-resistance of XCT machines.",
                "Lunch break",
                "Can imaging equipment drink coffee? There is only one way to find out!",
                "coffee",
                date(2022, 10, 2),
                date(2022, 10, 3),
                "~/documents/coffee/",
            ),
        )
        self.exec(
            "insert into project (title, project_type, summary, keyword, start_date, end_date, directory_path) values (%s, %s, %s, %s, %s, %s, %s);",
            (
                "Analysis of a bucket with nothing inside",
                "Detective work",
                "We are very confident there is nothing in this bucket, but we should check first.",
                "bucket",
                date(2022, 9, 15),
                date(2022, 10, 1),
                "~/documents/bucket/",
            ),
        )

        self.exec(
            "insert into project (title, project_type, summary, keyword, start_date, end_date, directory_path) values (%s, %s, %s, %s, %s, %s, %s);",
            (
                "Non-destructive pinata party",
                "Birthday",
                "Do sweets expire?",
                "deadpool",
                date(2022, 10, 30),
                date(2022, 10, 31),
                "~/documents/deadpool/",
            ),
        )

        self.exec(
            "insert into project (title, project_type, summary, keyword, start_date, end_date, directory_path) values (%s, %s, %s, %s, %s, %s, %s);",
            (
                "Titanic 2",
                "Research",
                "Directory James Cameron sees money to be made here.",
                "watch",
                date(2022, 9, 29),
                date(2023, 1, 31),
                "~/documents/titanic-watch/",
            ),
        )

        # Fake project-instrument links
        self.exec("delete from project_instrument")
        self.exec(
            """
            insert into project_instrument (instrument_id, project_id) values
                (
                    (select instrument_id from instrument where name = 'Rapiscan'),
                    (select project_id from project where title = 'The caffeine-resistance of XCT machines.')
                    
                ),
                (
                    (select instrument_id from instrument where name = 'Nikon'),
                    (select project_id from project where title = 'Analysis of a bucket with nothing inside')
                    
                ),
                (
                    (select instrument_id from instrument where name = 'Zeiss'),
                    (select project_id from project where title = 'Non-destructive pinata party')
                    
                ),
                (
                    (select instrument_id from instrument where name = 'Zeiss'),
                    (select project_id from project where title = 'Titanic 2')
                    
                );
        """
        )

        # Fake project-user links
        self.exec("delete from project_user")
        self.exec(
            """
            insert into project_user (user_id, project_id) values
                (
                    (select user_id from "user" where first_name = 'Amin'),
                    (select project_id from project where title = 'The caffeine-resistance of XCT machines.')
    
                ),
                (
                    (select user_id from "user" where first_name = 'Elizabeth'),
                    (select project_id from project where title = 'Analysis of a bucket with nothing inside')
    
                ),
                (
                    (select user_id from "user" where first_name = 'Tristan'),
                    (select project_id from project where title = 'Non-destructive pinata party')
    
                ),
                (
                    (select user_id from "user" where first_name = 'Elizabeth'),
                    (select project_id from project where title = 'Titanic 2')
    
                );
            """
        )

        # Fake scan-project links
        self.exec("delete from scan;")
        self.exec(
            "insert into scan (voltage, amperage, exposure, projections, voxel_size, filter_thick, filter_material, source_sample_distance, sample_detector_distance, lens_type, project_id) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,(select project_id from project where title = 'The caffeine-resistance of XCT machines.'));",
            (1, 1, 1, 3716, 1, "Very thick", "Glass?", 0.3, 0.6, "Big"),
        )
        self.exec(
            "insert into scan (voltage, amperage, exposure, projections, voxel_size, filter_thick, filter_material, source_sample_distance, sample_detector_distance, lens_type, project_id) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,(select project_id from project where title = 'Analysis of a bucket with nothing inside'));",
            (1, 2, 3, 3716, 4, "Very thick", "Glass?", 0.3, 0.5, "Medium"),
        )
        self.exec(
            "insert into scan (voltage, amperage, exposure, projections, voxel_size, filter_thick, filter_material, source_sample_distance, sample_detector_distance, lens_type, project_id) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,(select project_id from project where title = 'Non-destructive pinata party'));",
            (2, 1, 1, 3716, 1, "Very thin", "Glass?", 0.4, 0.5, "Small"),
        )
        self.exec(
            "insert into scan (voltage, amperage, exposure, projections, voxel_size, filter_thick, filter_material, source_sample_distance, sample_detector_distance, lens_type, project_id) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,(select project_id from project where title = 'Titanic 2'));",
            (3, 2, 3, 3716, 1, "Very thick", "Glass?", 0.3, 0.5, "Big"),
        )

        # Fake scan-sample links
        self.exec("delete from scan_sample;")
        self.exec(
            """
                        insert into scan_sample (sample_id, scan_id) values
                            (
                                (select sample_id from sample where name = 'Mug'),
                                (select scan_id from scan where project_id = (select project_id from project where title = 'The caffeine-resistance of XCT machines.'))
    
                            ),
                            (
                                (select sample_id from sample where name = 'Bucket (no head)'),
                                (select scan_id from scan where project_id = (select project_id from project where title = 'Analysis of a bucket with nothing inside'))
    
                            ),
                            (
                                (select sample_id from sample where name = 'Deadpool'),
                                (select scan_id from scan where project_id = (select project_id from project where title = 'Non-destructive pinata party'))
    
                            ),
                            (
                                (select sample_id from sample where name = 'Pocket watch'),
                                (select scan_id from scan where project_id = (select project_id from project where title = 'Titanic 2'))
    
                            );
                    """
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # When running postgres via Docker, localhost doesn't map to 127.0.0.1; WTF??
    CONFIG = "host=127.0.0.1 port=5432 dbname=tams user=postgres password=postgres"
    with DatabaseInitialiser(CONFIG) as db:
        db.init_db()
    print("Database initialised")
