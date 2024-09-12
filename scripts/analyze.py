#!/usr/bin/python

import os
import sys
import codecs
import subprocess

commits = list()
output_columns = ["email", "author"]
output_rows = []
repo=""

def parse_commit_msg(line, commit):
    if (line.startswith("commit")):
        commit["id"] = line.split(" ")[1].strip()
    elif (line.startswith("Author:")):
        commit["author"] = line.split("Author:")[1].strip()
    elif (line.startswith("Date:")):
        commit["date"] = line.split("Date:")[1].strip()
    elif ("-by:" in line):
        end_index = line.index("-by:") + 3
        key_word = line[:end_index].strip()
        commit[key_word] = line[end_index + 1:].strip()

def parse_log_file(git_raw_log):
    with codecs.open(git_raw_log, 'r', encoding='utf-8', errors='ignore') as fdata:
        lines = fdata.readlines()
        for line in lines:
            if (line.startswith("commit")):
                commit = {}
                commits.append(commit)
            parse_commit_msg(line, commit)

def filter_by_email(email):
    activities = list()
    for commit_info in commits:
        new_commit_info = {}
        for k,v in commit_info.items():
            new_commit_info[k] = v
            if(email in v):
                if (k == "author"):
                    commit_id = commit_info["id"]
                    ins_del_map = get_insertions_deletions(commit_id)
                    new_commit_info["insertions"] = ins_del_map.get("insertions", 0)
                    new_commit_info["deletions"] = ins_del_map.get("deletions", 0)
                activities.append(new_commit_info)
    activity_count = {
        "email" : email
    }
    for activity in activities:
        for k,v in activity.items():
            if (k == "author" and email in v):
                activity_count["author"] = activity_count.get("author", 0) + 1
            if (k == "insertions"):
                activity_count["insertions"] = activity_count.get("insertions", 0) + int(activity.get("insertions", 0))
            if (k == "deletions"):
                activity_count["deletions"] = activity_count.get("deletions", 0) + int(activity.get("deletions", 0))
            if (k.endswith("-by") and email in v):
                if k not in output_columns:
                    output_columns.append(k)
                activity_count[k] = activity_count.get(k, 0) + 1

    output_rows.append(activity_count)

def get_insertions_deletions(commit_id):
    commit = {
        "id":commit_id
    }
    res = subprocess.run(["./get_ins_del_lines.sh", repo, commit_id], capture_output=True, text=True)
    for res in res.stdout.split(","):
        if "insertions" in res:
            commit["insertions"] = res.strip().split(" ")[0]
        elif "deletions" in res:
            commit["deletions"] = res.strip().split(" ")[0]
        elif "files changed" in res:
            commit["files_changed"] = res.strip().split(" ")[0]
    return commit


def output_csv():
    output_columns.append("insertions")
    output_columns.append("deletions")
    print(','.join(output_columns))
    for output_row in output_rows:
        row = []
        for col in output_columns:
            row.append(str(output_row.get(col, 0)))
        print(",".join(row))

def generate_git_raw_log(date_range):
    start = date_range.split("-")[0]
    end = date_range.split("-")[1]
    res = subprocess.run(["./gen_git_raw_log.sh", repo, start, end], capture_output=True, text=True)

def main(git_raw_log, date_range, email_list):
    generate_git_raw_log(date_range)
    parse_log_file(git_raw_log)
    for email in email_list.split(","):
        filter_by_email(email)
    output_csv()

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python3 analysis.py repo_folder date_range email_list(split with comma)")
        exit(1)
    repo = sys.argv[1]
    email_list = ""
    git_raw_log = f"{repo}/raw_git.log"
    date_range = sys.argv[2]
    email_list = sys.argv[3]
    main(git_raw_log, date_range, email_list)
