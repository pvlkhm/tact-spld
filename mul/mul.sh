yosys mul.ys
yosys-abc -c "read_blif mul.blif; collapse; strash; rewrite; rewrite -l; collapse; write_pla mul.pla; collapse; write_eqn mul.eqn"
espresso mul.pla > mul_opt.pla
python3 ../pla2gal.py mul_opt.pla mul_opt.pld
python3 ../gal2num.py mul_opt.pld > report.txt