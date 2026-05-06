import pandas as pd

df = pd.read_csv("all_gopro_gloss_alignment_direct.csv")
dur_map = pd.read_csv("merged_s5_duration_check_final.tsv", sep="\t")
dur_dict = dict(zip(dur_map["folder"], dur_map["merged_duration_s"]))

def check(row):
    dur = dur_dict.get(row["folder"], None)
    issues = []

    if row["gopro_start_rel_s"] < 0:
        issues.append("start<0")
    if row["gopro_end_rel_s"] < 0:
        issues.append("end<0")
    if row["gopro_start_rel_s"] >= row["gopro_end_rel_s"]:
        issues.append("start>=end")

    if dur is not None:
        if row["gopro_start_rel_s"] > dur:
            issues.append("start>dur")
        if row["gopro_end_rel_s"] > dur:
            issues.append("end>dur")

    return ",".join(issues)

df["issues"] = df.apply(check, axis=1)

bad = df[df["issues"] != ""]

print("Total rows:", len(df))
print("Problem rows:", len(bad))
print("\nIssue breakdown:")
print(df["issues"].value_counts())

bad.to_csv("gloss_alignment_issues.csv", index=False)
print("\nSaved issues to gloss_alignment_issues.csv")
