#!/usr/bin/env python3
"""Queue, pull-system and SQC teaching calculations. No production-system I/O."""
import argparse
import json
import math
from engineering_calcs import finite


def integer(name, value):
    value=finite(name,value,positive=True)
    if not value.is_integer(): raise ValueError(f"{name} must be an integer")
    return int(value)


def mmc(arrival_per_hour, service_per_hour_each, servers=1):
    """Steady FIFO M/M/c with pooled identical servers, infinite buffer/no abandonment."""
    arrival=finite("arrival rate",arrival_per_hour,minimum=0)
    service=finite("service rate",service_per_hour_each,positive=True)
    c=integer("servers",servers)
    if c>10000: raise ValueError("teaching helper is bounded to 10000 servers")
    rho=arrival/(c*service)
    if rho>=1: raise ValueError("unstable queue: arrival must be below total service capacity")
    offered=arrival/service
    # Stable Erlang-B recurrence, then convert to Erlang C; avoids factorial overflow.
    erlang_b=1.0
    for n in range(1,c+1):
        erlang_b=offered*erlang_b/(n+offered*erlang_b)
    probability_wait=erlang_b/(1-rho+rho*erlang_b)
    wait=probability_wait/(c*service-arrival)
    system=wait+1/service
    return {"utilisation":rho,"probability_wait":probability_wait,"mean_queue_wait_h":wait,
            "mean_system_time_h":system,"mean_queue_items":arrival*wait,"mean_system_items":arrival*system}


def little_lead_time(wip, throughput_per_hour):
    """Matched flow populations/boundaries in a stable process; returns hours."""
    return finite("WIP",wip,minimum=0)/finite("throughput",throughput_per_hour,positive=True)


def kingman_wait(arrival_per_hour, mean_service_h, arrival_cv, service_cv):
    """Approximate stable G/G/1 queue waiting time, hours; model assumptions matter."""
    arrival=finite("arrival",arrival_per_hour,minimum=0)
    te=finite("service time",mean_service_h,positive=True)
    ca=finite("arrival CV",arrival_cv,minimum=0)
    cs=finite("service CV",service_cv,minimum=0)
    rho=arrival*te
    if rho>=1: raise ValueError("unstable queue: utilisation must be below 1")
    return .5*(ca*ca+cs*cs)*rho/(1-rho)*te


def kanban_cards(demand_per_hour, replenishment_h, container_units, safety_fraction):
    demand=finite("demand",demand_per_hour,minimum=0)
    lead=finite("replenishment time",replenishment_h,positive=True)
    container=integer("container units",container_units)
    safety=finite("safety allowance",safety_fraction,minimum=0)
    return math.ceil(demand*lead*(1+safety)/container)


def capability(lsl, usl, mean, sigma):
    lsl,usl,mean=finite("LSL",lsl),finite("USL",usl),finite("mean",mean)
    sigma=finite("sigma",sigma,positive=True)
    if usl<=lsl: raise ValueError("USL must exceed LSL")
    return {"cp":(usl-lsl)/(6*sigma),"cpk":min(usl-mean,mean-lsl)/(3*sigma)}


def zero_failure_upper_bound(trials, confidence=.95):
    n=integer("trials",trials)
    confidence=finite("confidence",confidence,positive=True)
    if confidence>=1: raise ValueError("confidence must be below 1")
    return -math.expm1(math.log1p(-confidence)/n)


def demo():
    return {"evidence":"calculated teaching scenarios; factory data and distribution assumptions unverified",
            "mm1_6_arrivals_8_service_per_hour":mmc(6,8),
            "mm2_10_arrivals_6_service_each_per_hour":mmc(10,6,2),
            "little_lead_time_h":little_lead_time(24,6),
            "kingman_wait_h":kingman_wait(6,.125,1,.5),
            "kanban_cards_illustrative_20_percent_allowance":kanban_cards(12,1.5,6,.2),
            "capability_assuming_stable_normal_process":capability(9.8,10.2,10.05,.04),
            "failure_probability_upper_95pct_zero_of_10":zero_failure_upper_bound(10),
            "failure_probability_upper_95pct_zero_of_59":zero_failure_upper_bound(59)}


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo",action="store_true")
    args=parser.parse_args()
    if args.demo: print(json.dumps(demo(),indent=2,allow_nan=False))
    else: parser.print_help()
