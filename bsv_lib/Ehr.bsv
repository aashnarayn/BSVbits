// Ephemeral History Register (Ehr) for BSVbits
// Inspired by MIT 6.004 / 6.175 Constructive Computer Architecture
// Allows intra-cycle bypassing / forwarding across rules and methods with well-defined port ordering:
//   ehr[0]._read < ehr[0]._write < ehr[1]._read < ehr[1]._write < ...

package Ehr;

import Vector::*;

typedef Vector#(n, Reg#(t)) Ehr#(numeric type n, type t);

module mkEhr#(t initVal)(Ehr#(n, t)) provisos(Bits#(t, sz));
    Reg#(t) r <- mkReg(initVal);
    Vector#(n, RWire#(t)) wires <- replicateM(mkUnsafeRWire);
    Vector#(n, Reg#(t)) ifc = newVector;

    (* fire_when_enabled, no_implicit_conditions *)
    rule canonicalize;
        t val = r;
        for (Integer i = 0; i < valueOf(n); i = i + 1) begin
            if (wires[i].wget matches tagged Valid .wval) begin
                val = wval;
            end
        end
        r <= val;
    endrule

    for (Integer i = 0; i < valueOf(n); i = i + 1) begin
        ifc[i] = interface Reg;
            method t _read();
                t val = r;
                for (Integer j = 0; j < i; j = j + 1) begin
                    if (wires[j].wget matches tagged Valid .wval) begin
                        val = wval;
                    end
                end
                return val;
            endmethod

            method Action _write(t x);
                wires[i].wset(x);
            endmethod
        endinterface;
    end

    return ifc;
endmodule

endpackage
