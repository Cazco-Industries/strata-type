Builders put deterministic outline-edit scripts in their own candidate's
`transforms/` directory and run them explicitly. The baseline has no design
transforms. `prepare.py` changes names, expands public feature includes and
converts source formats; it does not redesign contours. In the legacy Mono
metadata, invalid `featureNames` inside `cvXX` is translated to the valid
`cvParameters/FeatUILabelNameID` form. Substitution rules and labels are retained.
