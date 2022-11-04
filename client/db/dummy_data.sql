/*
 Populate the database with dummy data.
 Requires that tables already exist in database.
 Only use this for development and testing.
 Warning: this will delete all existing data in tables! Use with caution.
 */

/*
 Populate with fake instruments.
 */

delete from instrument;

insert into instrument (name, status)
values ('Nikon', 'Utterly destroyed'),
('Zeiss', 'Working fine'),
('Rapiscan', 'Someone spilt coffee on it');


/*
 Populate with fake samples.
 */

delete from sample;

insert into sample (name, size, material, confidentiality)
values ('Mug', 15, 'Ceramic', False),
('Bucket', 50, 'Steel', True),
('Deadpool', 25, 'Paper', False),
('Pocket watch', 5, 'Gold', False);


/*
 Populate with fake users.
 */

delete from "user";

insert into "user" (first_name, last_name, email_address)
values ('Amin', 'Garbout', 'amin.garbout@manchester.ac.uk'),
('Elizabeth', 'Evans', 'elizabeth.evans-5@manchester.ac.uk'),
('Tristan', 'Lowe', 'Tristan.Lowe@manchester.ac.uk');


/*
 Populate with dummy projects.
 */

delete from project;

insert into project (
    title, project_type, summary, keyword, start_date, end_date, directory_path
)
values (
    'The caffeine-resistance of XCT machines',
    'Lunch break',
    'Can imaging equipment drink coffee? There is only one way to find out!',
    'coffee',
    '2022-10-02',
    '2022-10-03',
    '~/documents/coffee/'
),
(
    'Analysis of a bucket with nothing inside',
    'Detective work',
    'Very confident there is nothing in this bucket, but we should check first.',
    'bucket',
    '2022-09-15',
    '2022-10-01',
    '~/documents/bucket/'
),
(
    'Non-destructive pinata party',
    'Birthday',
    'Do sweets expire?',
    'deadpool',
    '2022-10-30',
    '2022-10-31',
    '~/documents/deadpool/'
),
(
    'Titanic 2',
    'Research',
    'Directory James Cameron sees money to be made here.',
    'watch',
    '2022-09-29',
    '2023-01-31',
    '~/documents/titanic-watch/'
);


/*
 Populate with dummy project-user links.
 */

delete from project_user;

insert into project_user (user_id, project_id)
values (
    (select user_id from "user"
        where first_name = 'Amin'),
    (select project_id from project
        where title = 'The caffeine-resistance of XCT machines')
),
(
    (select user_id from "user"
        where first_name = 'Elizabeth'),
    (select project_id from project
        where title = 'Analysis of a bucket with nothing inside')
),
(
    (select user_id from "user"
        where first_name = 'Tristan'),
    (select project_id from project
        where title = 'Non-destructive pinata party')
),
(
    (select user_id from "user"
        where first_name = 'Elizabeth'),
    (select project_id from project
        where title = 'Titanic 2')
);


/*
 Populate with dummy scans.
 */

delete from scan;

insert into scan (
    voltage,
    amperage,
    exposure,
    projections,
    voxel_size,
    filter_thick,
    filter_material,
    source_sample_distance,
    sample_detector_distance,
    lens_type,
    project_id,
    instrument_id
)
values (
    1,
    1,
    1,
    3716,
    1,
    'Very thick',
    'Glass?',
    0.3,
    0.6,
    'Big',
    (
        select project_id
        from project where title = 'The caffeine-resistance of XCT machines'
    ),
    (select instrument_id from instrument where name = 'Nikon')
),
(
    1,
    2,
    3,
    3716,
    4,
    'Very thick',
    'Glass?',
    0.3,
    0.5,
    'Medium',
    (
        select project_id
        from project where title = 'Non-destructive pinata party'
    ),
    (select instrument_id from instrument where name = 'Zeiss')
),
(
    2,
    1,
    1,
    3716,
    1,
    'Very thin',
    'Glass?',
    0.4,
    0.5,
    'Small',
    (
        select project_id
        from project where title = 'Analysis of a bucket with nothing inside'
    ),
    (select instrument_id from instrument where name = 'Rapiscan')
),
(
    3,
    2,
    3,
    3716,
    1,
    'Very thick',
    'Glass?',
    0.3,
    0.5,
    'Big',
    (
        select project_id from project where title = 'Titanic 2'
    ),
    (select instrument_id from instrument where name = 'Zeiss')
);


/*
 Populate with dummy scan-sample links.
 */

delete from scan_sample;

insert into scan_sample (scan_id, sample_id)
values (
    (select sample_id from sample where name = 'Mug'),
    (
        select scan_id
        from
            scan
        where
            project_id = (
                select project_id
                from
                    project
                where title = 'The caffeine-resistance of XCT machines'
            )
    )
),
(
    (select sample_id from sample where name = 'Bucket'),
    (
        select scan_id
        from
            scan
        where
            project_id = (
                select project_id
                from
                    project
                where title = 'Analysis of a bucket with nothing inside'
            )
    )
),
(
    (select sample_id from sample where name = 'Deadpool'),
    (
        select scan_id
        from
            scan
        where
            project_id = (
                select project_id
                from project where title = 'Non-destructive pinata party'
            )
    )
),
(
    (select sample_id from sample where name = 'Pocket watch'),
    (
        select scan_id
        from
            scan
        where
            project_id = (
                select project_id from project where title = 'Titanic 2'
            )
    )

);
