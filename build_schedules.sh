#!/bin/bash


function build_schedules() {
  comp=$1

  for tex in schedules/${comp}/tex/*.tex; do
    echo "Generating schedule PDF for ${comp} team ${tex}..."
    pdflatex -output-directory schedules/${comp} "$tex"
  done

  rm schedules/${comp}/*.aux schedules/${comp}/*.log
}

comps=("bio" "aero" "civil" "meche" "chem" "cs")
for comp in ${comps[@]}; do
  rm schedules/${comp}/*.pdf
  build_schedules $comp
done
