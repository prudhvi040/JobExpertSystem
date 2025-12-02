# job_advisor_experta.py
# Compatibility shim (must run before importing experta)
import collections
import collections.abc
setattr(collections, "Mapping", collections.abc.Mapping)
setattr(collections, "MutableMapping", collections.abc.MutableMapping)
setattr(collections, "Sequence", collections.abc.Sequence)

# Now safe to import experta
from experta import KnowledgeEngine, Fact, Field, Rule, MATCH

class Profile(Fact):
    prefers_indoor = Field(bool, default=False)
    prefers_outdoor = Field(bool, default=False)
    prefers_hybrid = Field(bool, default=False)
    stable_schedule = Field(bool, default=False)
    remote_ok = Field(bool, default=False)
    education = Field(str, default="None")
    skill_match = Field(float, default=0.0)
    years_experience = Field(int, default=0)
    high_physical = Field(bool, default=False)
    willing_shifts = Field(bool, default=False)
    has_driving_license = Field(bool, default=False)
    salary_expectation = Field(float, default=0.0)

class Recommendation(Fact):
    job = Field(str, mandatory=True)
    reason = Field(str, default="")

class JobAdvisorEngine(KnowledgeEngine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.salary_low = 2000
        self.salary_med = 4000
        self.reasons = []

    @Rule(Profile(prefers_hybrid=True), salience=90)
    def prefer_hybrid(self):
        self.declare(Fact(branch='hybrid'))
        self.reasons.append("Branch: hybrid")

    @Rule(Profile(prefers_indoor=True), ~Fact(branch=MATCH.any), salience=80)
    def prefer_indoor(self):
        self.declare(Fact(branch='indoor'))
        self.reasons.append("Branch: indoor")

    @Rule(Profile(prefers_outdoor=True), ~Fact(branch=MATCH.any), salience=70)
    def prefer_outdoor(self):
        self.declare(Fact(branch='outdoor'))
        self.reasons.append("Branch: outdoor")

    @Rule(Fact(branch='indoor'), Profile(stable_schedule=True, salary_expectation=MATCH.s))
    def indoor_admin(self, s):
        if s < self.salary_med:
            self.declare(Recommendation(job="ADMIN",
                                        reason="Indoor + stable + modest salary"))
            self.reasons.append("Rule: indoor_admin")

    @Rule(Fact(branch='indoor'),
          Profile(remote_ok=True, skill_match=MATCH.sm, salary_expectation=MATCH.s))
    def indoor_remote_it(self, sm, s):
        if sm >= 0.6:
            if s >= self.salary_med:
                self.declare(Recommendation(job="IT", reason="Remote+skilled+med/high salary -> IT"))
                self.reasons.append("Rule: indoor_remote_it -> IT")
            else:
                self.declare(Recommendation(job="REMOTE/FREELANCE",
                                            reason="Remote+skilled+lower salary -> FREELANCE"))
                self.reasons.append("Rule: indoor_remote_it -> REMOTE/FREELANCE")

    @Rule(Fact(branch='indoor'), ~Recommendation(job=MATCH.any))
    def indoor_fallback_it(self):
        self.declare(Recommendation(job="IT", reason="Indoor fallback -> IT"))
        self.reasons.append("Rule: indoor_fallback_it")

    @Rule(Fact(branch='hybrid'),
          Profile(skill_match=MATCH.sm, years_experience=MATCH.y, remote_ok=MATCH.r))
    def hybrid_rules(self, sm, y, r):
        if sm > 0.6 and y > 2:
            if r:
                self.declare(Recommendation(job="REMOTE/FREELANCE",
                                            reason="Hybrid+skill+exp+remote -> FREELANCE"))
                self.reasons.append("Rule: hybrid -> FREELANCE")
            else:
                self.declare(Recommendation(job="IT", reason="Hybrid+skill -> IT"))
                self.reasons.append("Rule: hybrid -> IT")
        elif y >= 1:
            self.declare(Recommendation(job="IT", reason="Hybrid some experience -> IT"))
            self.reasons.append("Rule: hybrid fallback -> IT")
        else:
            self.declare(Recommendation(job="ADMIN", reason="Hybrid low experience -> ADMIN"))
            self.reasons.append("Rule: hybrid fallback -> ADMIN")

    @Rule(Fact(branch='outdoor'),
          Profile(high_physical=True, has_driving_license=True, willing_shifts=True))
    def outdoor_delivery_full(self):
        self.declare(Recommendation(job="DELIVERY",
                                    reason="Outdoor+physical+driving+shifts -> DELIVERY"))
        self.reasons.append("Rule: outdoor_delivery_full")

    @Rule(Fact(branch='outdoor'), Profile(willing_shifts=True), salience=10)
    def outdoor_delivery_shifts(self):
        self.declare(Recommendation(job="DELIVERY", reason="Willing for shifts -> DELIVERY"))
        self.reasons.append("Rule: outdoor_delivery_shifts")

    @Rule(Fact(branch='outdoor'), ~Recommendation(job=MATCH.any))
    def outdoor_sales(self):
        self.declare(Recommendation(job="SALES", reason="Outdoor -> SALES"))
        self.reasons.append("Rule: outdoor_sales")

    @Rule(Recommendation(job="ADMIN"), Profile(salary_expectation=MATCH.s))
    def admin_salary_adjust(self, s):
        if s > self.salary_med:
            self.declare(Recommendation(job="IT", reason="Admin salary high -> IT"))
            self.reasons.append("Rule: admin_salary_adjust -> IT")

    @Rule(Recommendation(job="IT"), Profile(skill_match=MATCH.sm))
    def it_skill_check(self, sm):
        if sm < 0.4:
            self.declare(Recommendation(job="ADMIN", reason="Low skill match -> ADMIN"))
            self.reasons.append("Rule: it_skill_check -> ADMIN")

def advise(profile: dict):
    engine = JobAdvisorEngine()
    engine.reset()
    engine.declare(Profile(**profile))
    engine.run()
    # pick most specific Recommendation fact (last declared)
    rec = None
    for f in engine.facts.values():
        if isinstance(f, Recommendation):
            rec = f
    return rec, engine.reasons

if __name__ == "__main__":
    sample = {
        "prefers_indoor": True,
        "prefers_outdoor": False,
        "prefers_hybrid": False,
        "stable_schedule": True,
        "remote_ok": False,
        "education": "Bachelors",
        "skill_match": 0.3,
        "years_experience": 1,
        "salary_expectation": 1800.0
    }
    recommendation, trace = advise(sample)
    print("Recommendation:", dict(recommendation) if recommendation else None)
    print("Trace:", trace)
