select * from domains order by timestamp desc limit 10;

CREATE TABLE domains (
    id serial PRIMARY KEY,
    domain varchar (256) NOT NULL,
    base_domain varchar (256) NOT NULL,
    domain_name varchar (256) NOT NULL,
    domain_ip varchar (256),
    as_number integer,
    as_subnet varchar (256),
    as_name varchar (256),
    nameserver varchar (256),
    ns_base_domain varchar (256),
    ns_domain_ip varchar (256),
    ns_as_number integer,
    ns_as_subnet varchar (256),
    ns_as_name varchar (256),
    insert_date date
);