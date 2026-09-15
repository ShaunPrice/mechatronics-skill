// Original bounded native Xcos simulation/CSV comparison. MIT.
// Runs without graphics using scicos_simulate(...,"nw") and TOWS_c.
export_dir = get_absolute_file_path("xcos_batch.sce");
exec(export_dir + "xcos_build.sce", -1);
clear mech_export_record;
simulation_info = scicos_simulate(selected_plant_diagram, list(), struct(), "nw");
if exists("mech_export_record") == 0 then error("Native recorder produced no result."); end
record_times = mech_export_record.time;
record_values = mech_export_record.values;
if size(record_times,"*") < 1 then error("Native recorder returned no samples."); end
csvWrite([record_times, record_values], export_dir + "xcos_response.csv", ",", ".", "%.17g");
reference = csvRead(export_dir + "reference.csv", ",", ".");
reference_indices = round(record_times/sample_dt) + 1;
if max(abs(record_times - (reference_indices-1)*sample_dt)) > 1d-8 then
    error("Native recording times do not match the comparison grid.");
end
if min(reference_indices) < 1 | max(reference_indices) > size(reference,1) then
    error("Native recording times exceed the exported reference.");
end
xcos_output_error = max(abs(record_values - reference(reference_indices,3)));
mprintf("Native Xcos samples: %d; first/last time: %.9g / %.9g s\n", size(record_times,"*"), record_times(1), record_times($));
mprintf("Maximum native Xcos output difference versus Python RK4: %.9g\n", xcos_output_error);
// An event at exactly final_time may be excluded; compare only recorded times.
// The resulting CSV has two columns (time_s, output), without a header.
