
module propabmaker #(
  parameter L2N = 3, parameter [L2N-1:0] T = 3
) (
    input[L2N-1:0] randint, output propbit
);
    assign propbit = (randint >= T );
endmodule

