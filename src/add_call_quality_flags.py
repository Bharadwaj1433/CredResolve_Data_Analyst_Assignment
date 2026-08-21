import pandas as pd

raw = pd.read_csv("data/raw/calls.csv")
clean = pd.read_csv("data/cleaned/calls.csv")

conflict_ids = []

for call_id, group in raw.groupby("call_id"):
    if len(group) > 1:
        agent_conflict = group["agent_id"].nunique(dropna=False) > 1
        event_conflict = group["event_at"].nunique(dropna=False) > 1

        if agent_conflict or event_conflict:
            conflict_ids.append(call_id)

clean["call_id_conflict"] = clean["call_id"].isin(conflict_ids)

agent_conflict_ids = set()

event_conflict_ids = set()

for call_id, group in raw.groupby("call_id"):
    if len(group) > 1:
        if group["agent_id"].nunique(dropna=False) > 1:
            agent_conflict_ids.add(call_id)

        if group["event_at"].nunique(dropna=False) > 1:
            event_conflict_ids.add(call_id)

clean["agent_id_conflict"] = clean["call_id"].isin(agent_conflict_ids)
clean["event_at_conflict"] = clean["call_id"].isin(event_conflict_ids)

clean.to_csv(
    "data/cleaned/calls.csv",
    index=False
)

print("Clean rows:", len(clean))
print("Call conflict IDs:", len(conflict_ids))
print("Agent conflict IDs:", len(agent_conflict_ids))
print("Event conflict IDs:", len(event_conflict_ids))
print("Output:", "data/cleaned/calls.csv")
