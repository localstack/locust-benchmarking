#!/usr/bin/env python

import argparse
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="+")
    args = parser.parse_args()



    stats = []
    for file in args.file:
        df = pd.read_csv(file)
        for _, row in df.iterrows():
            if row["Name"] != "Aggregated":
                continue

            rps = row["Requests/s"]
            p50 = row["50%"]
            p99 = row["99%"]


            stats.append({
                "filename": file,
                "name": "Requests per second",
                "stat": rps,
            })
            stats.append({
                "filename": file,
                "name": "p50 [ms]",
                "stat": p50,
            })
            stats.append({
                "filename": file,
                "name": "p99 [ms]",
                "stat": p99,
            })
    df = pd.DataFrame(stats)

    fig = make_subplots(rows=2, cols=2)

    # rps
    def plot_selector(selector: str, *, row: int, col: int):
        data = df[df["name"] == selector]
        fig.add_trace(
                go.Bar(x=data["filename"], y=data["stat"], text=data["name"], name=selector),
                row=row, col=col,
        )

    plot_selector("Requests per second", row=1, col=1)
    plot_selector("p50 [ms]", row=1, col=2)
    plot_selector("p99 [ms]", row=2, col=1)

    fig.update_layout()

    fig.show()
