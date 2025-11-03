#!/usr/bin/env bash

declare -A results

results["01/self-test_diagnostic"]="83 83 83"
results["01/self-test_diagnostic_busy_loop"]="311963 311963 311963"
results["02/signal_amplifier"]="160 160 160"
results["02/signal_amplifier_parallelize"]="84 84 84"
results["03/differential_converter"]="200 200 200"
results["03/differential_converter_multithreaded"]="263 263 263"
results["04/signal_comparator"]="278 278 278"
results["04/signal_comparator_unconditional"]="319 319 319"
results["05/signal_multiplexer"]="410 422 401"
results["06/sequence_generator"]="173 173 173"
results["07/sequence_counter"]="340 340 336"
results["07/sequence_counter_no_backup"]="347 347 349"
results["08/signal_edge_detector"]="435 437 437"
results["09/interrupt_handler"]="310 312 310"
results["10/signal_pattern_detector"]="377 389 384"
results["11/sequence_peak_detector"]="464 470 472"
results["12/sequence_reverser"]="450 444 438"
results["12/sequence_reverser_no_memory"]="544 592 614"
results["13/signal_multiplier"]="3428 3393 3196"
results["14/image_test_pattern_1"]="2352"
results["15/image_test_pattern_2"]="3609"
results["16/exposure_mask_viewer"]="752 592 616"
results["17/histogram_viewer"]="2527 1847 1423"
results["18/signal_window_filter"]="2371 2371 2371"
results["19/signal_divider"]="5696 6072 7184"
results["20/sequence_indexer"]="2533 2243 2263"
results["21/sequence_sorter"]="4223 3894 4291"
results["22/stored_image_decoder"]="3394 3218 3398"

for puzzle in $(printf "%s\n" "${!results[@]}" | sort); do
	folder=$(dirname $puzzle)
	read -a expected <<< "${results[$puzzle]}"

	if (( ${#expected[@]} == 1 )); then
		result="$(python tis100.py "test/$puzzle.txt" -l "test/$folder/layout.txt")"
		if echo "$result" | grep -q "Test passed" && echo "$result" | grep -q "Completed in ${expected[0]}"; then
			echo "PASS: $puzzle"
		else
			echo "FAIL: $puzzle"
		fi
	else
		for ((i=0; i<${#expected[@]}; i++)); do
			layout="layout$((i+1))"
			result="$(python tis100.py "test/$puzzle.txt" -l "test/$folder/${layout}.txt")"
			if echo "$result" | grep -q "Test passed" && echo "$result" | grep -q "Completed in ${expected[$i]}"; then
				echo "PASS: $puzzle ($layout)"
			else
				echo "FAIL: $puzzle ($layout)"
			fi
		done
	fi
done
