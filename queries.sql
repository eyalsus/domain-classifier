-- average per classifier
select label, count(1),avg(mlmodel_xgbclassifier), avg(mlmodel_logisticregression), avg(snamodel), avg(markovmodel)
from domains 
where train_date is not null
group by label;

-- markov model
select *
from domains 
where train_date is not null
and markovmodel = 1;

select *
from domains
where timestamp > NOW() - INTERVAL '3 DAY'
order by timestamp  desc
limit 100;

-- delete
-- from domains
-- where timestamp > NOW() - INTERVAL '1 DAY'