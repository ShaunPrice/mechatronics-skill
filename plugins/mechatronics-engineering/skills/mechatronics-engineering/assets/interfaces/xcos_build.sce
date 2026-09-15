// Original native diagram construction. MIT. Calls installed Scilab/Xcos APIs.
// Tested against Scilab 2026.1.0; no full browser graph/controller conversion.
export_dir = get_absolute_file_path("xcos_build.sce");
loadXcosLibs();
exec(export_dir + "plant_data.sce", -1);

selected_plant_diagram = scicos_diagram();
selected_plant_diagram.props.title = "Selected plant - workspace recording";
selected_plant_diagram.props.tf = final_time;
// Absolute/relative/time tolerance, max interval, real-time scale, solver, max step.
selected_plant_diagram.props.tol = [1d-10, 1d-8, 1d-10, 100001, 0, 1, sample_dt];
selected_plant_diagram.props.context = mgetl(export_dir + "plant_data.sce");

source_block = STEP_FUNCTION("define");
source_block.graphics.orig = [20, 180];
source_block.graphics.sz = [60, 40];
source_block.graphics.pout = 5;
// STEP_FUNCTION is a native superblock; locate its STEP by GUI identifier.
for block_index = 1:length(source_block.model.rpar.objs)
    inner_block = source_block.model.rpar.objs(block_index);
    if typeof(inner_block) == "Block" then
        if inner_block.gui == "STEP" then
            inner_block.graphics.exprs = ["0"; "0"; "1"];
            inner_block.model.firing = 0;
            inner_block.model.rpar = [1; 1];
            source_block.model.rpar.objs(block_index) = inner_block;
        end
    end
end

plant_block = CLSS("define");
plant_block.graphics.orig = [180, 180];
plant_block.graphics.sz = [80, 50];
plant_block.graphics.pin = 5;
plant_block.graphics.pout = 6;
plant_block.graphics.exprs = [sci2exp(A); sci2exp(B); sci2exp(C); sci2exp(D); sci2exp(x0)];
plant_block.model.state = x0(:);
plant_block.model.rpar = [A(:); B(:); C(:); D(:)];

record_block = TOWS_c("define");
record_block.graphics.orig = [380, 180];
record_block.graphics.sz = [80, 50];
record_block.graphics.pin = 6;
record_block.graphics.pein = 7;
record_buffer_size = ceil(final_time/sample_dt) + 2;
record_block.graphics.exprs = [string(record_buffer_size); "mech_export_record"; "0"];
record_block.model.ipar = [record_buffer_size; length("mech_export_record"); ascii("mech_export_record")'];

clock_block = CLOCK_c("define");
clock_block.graphics.orig = [380, 320];
clock_block.graphics.sz = [60, 40];
clock_block.graphics.peout = 7;
for block_index = 1:length(clock_block.model.rpar.objs)
    inner_block = clock_block.model.rpar.objs(block_index);
    if typeof(inner_block) == "Block" then
        if inner_block.gui == "EVTDLY_c" then
            inner_block.graphics.exprs = [sci2exp(sample_dt); "0"];
            inner_block.model.rpar = [sample_dt; 0];
            inner_block.model.firing = 0;
            clock_block.model.rpar.objs(block_index) = inner_block;
        end
    end
end

selected_plant_diagram.objs = list(source_block, plant_block, record_block, clock_block);
selected_plant_diagram.objs(5) = scicos_link(xx=[80;180], yy=[200;205], ct=[1,1], from=[1,1,0], to=[2,1,1]);
selected_plant_diagram.objs(6) = scicos_link(xx=[260;380], yy=[205;205], ct=[1,1], from=[2,1,0], to=[3,1,1]);
selected_plant_diagram.objs(7) = scicos_link(xx=[410;420], yy=[320;230], ct=[5,-1], from=[4,1,0], to=[3,1,1]);

// A second native diagram presents the same output through an interactive scope.
selected_plant_scope_diagram = selected_plant_diagram;
selected_plant_scope_diagram.props.title = "Selected plant - scope";
scope_block = CSCOPE("define");
scope_block.graphics.orig = [380, 180];
scope_block.graphics.sz = [80, 50];
scope_block.graphics.pin = 6;
scope_block.graphics.pein = 7;
reference = csvRead(export_dir + "reference.csv", ",", ".");
scope_margin = max(0.1, 0.1*(max(reference(:,3))-min(reference(:,3))));
scope_min = min(reference(:,3)) - scope_margin;
scope_max = max(reference(:,3)) + scope_margin;
scope_block.model.rpar = [0; scope_min; scope_max; final_time];
scope_block.graphics.exprs(5) = sci2exp(scope_min);
scope_block.graphics.exprs(6) = sci2exp(scope_max);
scope_block.graphics.exprs(7) = sci2exp(final_time);
selected_plant_scope_diagram.objs(3) = scope_block;

// Scilab-native serialization is available in CLI too; this is not a .zcos file.
save(export_dir + "selected-plant.sod", "selected_plant_diagram", "selected_plant_scope_diagram");
mprintf("Constructed native selected-plant recording and scope diagrams.\n");
