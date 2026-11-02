# Evaluation

`make reproduce` runs the fixed seeded scheduler workload and the generated vision/text
duplicate-detection cases. It rewrites the Python/TypeScript parity fixture and
`site/src/data/results.generated.json`; the site displays only the resulting metrics.

The cluster measurements are simulated scheduling behavior, not production throughput.
Vision inputs are synthetic geometric images transformed by resizing, cropping, brightness
changes, and JPEG encoding. Text inputs are generated English, French, and Hindi sentences
with small edits plus unrelated negatives. Precision and recall are pairwise and reflect
these small fixtures only; they do not establish general detection quality. The text report
uses MinHash signatures and a fixed similarity cutoff, not an external language model.
The browser DAG builder uses fixed illustrative stage durations; it is not a measured ETA.
The chunk-size estimate is a deterministic model with assumed per-task overhead and input
throughput; it is not an empirical calibration against a live cluster.
