/*
 Populate with fake instruments.
 */

delete
from instrument;

insert into instrument (name, status)
values ('Nikon', 'Utterly destroyed'),
('Zeiss', 'Working fine'),
('Rapiscan', 'Someone spilt coffee on it');


/*
 Populate with fake samples.
 */

insert into sample (name, size, material, confidentiality)
values ('Mug', 15, 'Ceramic', False),
('Bucket', 50, 'Steel', True),
('Deadpool', 25, 'Paper', False),
('Pocket watch', 5, 'Gold', False);
