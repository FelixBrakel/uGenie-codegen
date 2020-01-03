library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use IEEE.math_real."ceil";
use IEEE.math_real."log2";

entity add_3_tb is
end add_3_tb;

architecture behave of add_3_tb is
    constant c_CLOCK_PERIOD : time := 50 ns;
    signal r_CLOCK: std_logic :='0';
    signal r_i_FU : std_logic_vector((32*5)-1 downto 0);
    signal w_o_FU : std_logic_vector((32*1)-1 downto 0);
    signal r_r_COMPUTING : std_logic := '0';
    signal r_r_LOAD_INST : std_logic := '0';
    signal r_r_LOAD_NEXT_INST : std_logic := '0';
    signal r_r_INPUT_INST : std_logic_vector(26 downto 0);
    signal r_r_RESET : std_logic :='0';
        --BEGIN DEBUG SIGNALS
    signal w_w_SEL_MUXA : std_logic_vector(1 downto 0);
    signal w_w_SEL_MUXB : std_logic_vector(1 downto 0);
    signal w_w_MUXA_OUT : std_logic_vector(31 downto 0);
    signal w_w_MUXB_OUT : std_logic_vector(31 downto 0);
    signal w_d_in_cb_out1_sel : natural range 0 to 4-1;
    signal w_d_in_cb_out2_sel : natural range 0 to 4-1;
    signal w_d_in_cb_out3_sel : natural range 0 to 4-1;
    signal w_d_input_crossbar_out1 : std_logic_vector(31 downto 0);
    signal w_d_input_crossbar_out2 : std_logic_vector(31 downto 0);
    signal w_d_input_crossbar_out3 : std_logic_vector(31 downto 0);
        --END DEBUG SIGNALS
    component FU is
        generic (
                    INSTRUCTIONS : natural;
                    TOTAL_EXE_CYCLES : natural;
                    BITWIDTH : natural; -- 31 -> meaning 32
                    RF_DEPTH: natural; --15 -> meaning 16
                    INPUT_PORTS : natural;
                    OUTPUT_PORTS : natural;
                    OPCODE :natural;
                    IS_MUL: natural
                );
        port(
            i_clock : in std_logic;
            --specify inputs (number of FUs that sends input to this FU)
           -- i_FU : in std_logic_vector(((BITWIDTH +1)*INPUT_PORTS)-1 downto 0);
            
            i_FU : in std_logic_vector(((BITWIDTH +1)*INPUT_PORTS)- 
            IS_MUL*((BITWIDTH +1)/2*INPUT_PORTS)   -1
            downto 0);
            --i_FU : in std_logic_vector(natural(real(IS_MUL)/real(2)*real(BITWIDTH +1)*real(INPUT_PORTS))-1 downto 0);
            --specify outputs (number of FUs that this FU can send the output to)
            o_FU : out std_logic_vector(((BITWIDTH +1)*OUTPUT_PORTS)-1 downto 0);
            -- SIGNALS FOR INSTRUCTION MEMORY
            r_COMPUTING : in std_logic;
            r_LOAD_INST: in std_logic := '0';
            r_LOAD_NEXT_INST: in std_logic ;
            r_INPUT_INST : in std_logic_vector(
                natural(ceil(log2(real(TOTAL_EXE_CYCLES+1))))+ -- bit required to ID Clock
                natural(ceil(log2(real(INPUT_PORTS))))*3 + -- crossbar Select Bits
                2 + -- Register Write enable bits (input 1 and input 2) 
                natural(ceil(log2(real(RF_DEPTH+1)))) * 4 + -- RF select bits
                4 -- Select signals for MuxA and MuxB
                -1
                downto 0);
            r_RESET : in std_logic
            );
    end component FU;
begin
    --instantiate the Unit Under Test (UUT)
    UUT: FU
        generic map (
            INSTRUCTIONS => 3,
            BITWIDTH => 31,
            RF_DEPTH => 1,
            INPUT_PORTS => 5,
            OUTPUT_PORTS => 1,
            TOTAL_EXE_CYCLES => 255,
            OPCODE => 0,
            IS_MUL => 0
        )
        port map(
            i_clock => r_CLOCK,
            i_FU => r_i_FU,
            o_FU => w_o_FU,
            r_COMPUTING => r_r_COMPUTING,
            r_LOAD_INST => r_r_LOAD_INST,
            r_LOAD_NEXT_INST => r_r_LOAD_NEXT_INST,
            r_INPUT_INST => r_r_INPUT_INST,
            r_RESET => r_r_RESET

                );

    p_CLK_GEN: process is
    begin
        wait for c_CLOCK_PERIOD/2;
        r_CLOCK <= not r_CLOCK;
    end process p_CLK_GEN;

    process
    begin
        r_r_LOAD_INST <= '1';
        r_r_INPUT_INST <= "100011010000000011000000000";
        r_r_LOAD_NEXT_INST <= '1';
        wait for 50 ns;
        r_r_LOAD_INST <= '1';
        r_r_INPUT_INST <= "100011110100110000000000101";
        r_r_LOAD_NEXT_INST <= '1';
        wait for 50 ns;
        r_r_LOAD_INST <= '1';
        r_r_INPUT_INST <= "100100000000000000000000001";
        r_r_LOAD_NEXT_INST <= '1';
        wait for 50 ns;
        r_r_LOAD_INST <= '1';
        r_r_INPUT_INST <= "100100010000000000000001000";
        r_r_LOAD_NEXT_INST <= '0';
        wait for 50 ns;
        r_r_LOAD_INST <= '0';
        r_r_COMPUTING <= '1';
        -- 0
        wait for 50 ns;
        -- 1
        wait for 50 ns;
        -- 2
        wait for 50 ns;
        -- 3
        wait for 50 ns;
        -- 4
        wait for 50 ns;
        -- 5
        wait for 50 ns;
        -- 6
        wait for 50 ns;
        -- 7
        wait for 50 ns;
        -- 8
        wait for 50 ns;
        -- 9
        wait for 50 ns;
        -- 10
        wait for 50 ns;
        -- 11
        wait for 50 ns;
        -- 12
        wait for 50 ns;
        -- 13
        wait for 50 ns;
        -- 14
        wait for 50 ns;
        -- 15
        wait for 50 ns;
        -- 16
        wait for 50 ns;
        -- 17
        wait for 50 ns;
        -- 18
        wait for 50 ns;
        -- 19
        wait for 50 ns;
        -- 20
        wait for 50 ns;
        -- 21
        wait for 50 ns;
        -- 22
        wait for 50 ns;
        -- 23
        wait for 50 ns;
        -- 24
        wait for 50 ns;
        -- 25
        wait for 50 ns;
        -- 26
        wait for 50 ns;
        -- 27
        wait for 50 ns;
        -- 28
        wait for 50 ns;
        -- 29
        wait for 50 ns;
        -- 30
        wait for 50 ns;
        -- 31
        wait for 50 ns;
        -- 32
        wait for 50 ns;
        -- 33
        wait for 50 ns;
        -- 34
        wait for 50 ns;
        -- 35
        wait for 50 ns;
        -- 36
        wait for 50 ns;
        -- 37
        wait for 50 ns;
        -- 38
        wait for 50 ns;
        -- 39
        wait for 50 ns;
        -- 40
        wait for 50 ns;
        -- 41
        wait for 50 ns;
        -- 42
        wait for 50 ns;
        -- 43
        wait for 50 ns;
        -- 44
        wait for 50 ns;
        -- 45
        wait for 50 ns;
        -- 46
        wait for 50 ns;
        -- 47
        wait for 50 ns;
        -- 48
        wait for 50 ns;
        -- 49
        wait for 50 ns;
        -- 50
        wait for 50 ns;
        -- 51
        wait for 50 ns;
        -- 52
        wait for 50 ns;
        -- 53
        wait for 50 ns;
        -- 54
        wait for 50 ns;
        -- 55
        wait for 50 ns;
        -- 56
        wait for 50 ns;
        -- 57
        wait for 50 ns;
        -- 58
        wait for 50 ns;
        -- 59
        wait for 50 ns;
        -- 60
        wait for 50 ns;
        -- 61
        wait for 50 ns;
        -- 62
        wait for 50 ns;
        -- 63
        wait for 50 ns;
        -- 64
        wait for 50 ns;
        -- 65
        wait for 50 ns;
        -- 66
        wait for 50 ns;
        -- 67
        wait for 50 ns;
        -- 68
        wait for 50 ns;
        -- 69
        wait for 50 ns;
        -- 70
        wait for 50 ns;
        -- 71
        wait for 50 ns;
        -- 72
        wait for 50 ns;
        -- 73
        wait for 50 ns;
        -- 74
        wait for 50 ns;
        -- 75
        wait for 50 ns;
        -- 76
        wait for 50 ns;
        -- 77
        wait for 50 ns;
        -- 78
        wait for 50 ns;
        -- 79
        wait for 50 ns;
        -- 80
        wait for 50 ns;
        -- 81
        wait for 50 ns;
        -- 82
        wait for 50 ns;
        -- 83
        wait for 50 ns;
        -- 84
        wait for 50 ns;
        -- 85
        wait for 50 ns;
        -- 86
        wait for 50 ns;
        -- 87
        wait for 50 ns;
        -- 88
        wait for 50 ns;
        -- 89
        wait for 50 ns;
        -- 90
        wait for 50 ns;
        -- 91
        wait for 50 ns;
        -- 92
        wait for 50 ns;
        -- 93
        wait for 50 ns;
        -- 94
        wait for 50 ns;
        -- 95
        wait for 50 ns;
        -- 96
        wait for 50 ns;
        -- 97
        wait for 50 ns;
        -- 98
        wait for 50 ns;
        -- 99
        wait for 50 ns;
        -- 100
        wait for 50 ns;
        -- 101
        wait for 50 ns;
        -- 102
        wait for 50 ns;
        -- 103
        wait for 50 ns;
        -- 104
        wait for 50 ns;
        -- 105
        wait for 50 ns;
        -- 106
        wait for 50 ns;
        -- 107
        wait for 50 ns;
        -- 108
        wait for 50 ns;
        -- 109
        wait for 50 ns;
        -- 110
        wait for 50 ns;
        -- 111
        wait for 50 ns;
        -- 112
        wait for 50 ns;
        -- 113
        wait for 50 ns;
        -- 114
        wait for 50 ns;
        -- 115
        wait for 50 ns;
        -- 116
        wait for 50 ns;
        -- 117
        wait for 50 ns;
        -- 118
        wait for 50 ns;
        -- 119
        wait for 50 ns;
        -- 120
        wait for 50 ns;
        -- 121
        wait for 50 ns;
        -- 122
        wait for 50 ns;
        -- 123
        wait for 50 ns;
        -- 124
        wait for 50 ns;
        -- 125
        wait for 50 ns;
        -- 126
        wait for 50 ns;
        -- 127
        wait for 50 ns;
        -- 128
        wait for 50 ns;
        -- 129
        wait for 50 ns;
        -- 130
        wait for 50 ns;
        -- 131
        wait for 50 ns;
        -- 132
        wait for 50 ns;
        -- 133
        wait for 50 ns;
        -- 134
        wait for 50 ns;
        -- 135
        wait for 50 ns;
        -- 136
        wait for 50 ns;
        -- 137
        wait for 50 ns;
        -- 138
        wait for 50 ns;
        -- 139
        wait for 50 ns;
        r_i_FU <= "0000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000";
        -- 140
        wait for 50 ns;
        -- 141
        wait for 50 ns;
        r_i_FU <= "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000100000000000000000000000000000000";
        -- 142
        wait for 50 ns;
        -- 143
        wait for 50 ns;
        r_i_FU <= "0000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000";
        -- 144
        wait for 50 ns;
        -- 145
        wait for 50 ns;
        -- 146
        wait for 50 ns;
        -- 147
        wait for 50 ns;
        -- 148
        wait for 50 ns;
        -- 149
        wait for 50 ns;
        -- 150
        wait for 50 ns;
        -- 151
        wait for 50 ns;
        -- 152
        wait for 50 ns;
        -- 153
        wait for 50 ns;
        -- 154
        wait for 50 ns;
        -- 155
        wait for 50 ns;
        -- 156
        wait for 50 ns;
        -- 157
        wait for 50 ns;
        -- 158
        wait for 50 ns;
        -- 159
        wait for 50 ns;
        -- 160
        wait for 50 ns;
        -- 161
        wait for 50 ns;
        -- 162
        wait for 50 ns;
        -- 163
        wait for 50 ns;
        -- 164
        wait for 50 ns;
        -- 165
        wait for 50 ns;
        -- 166
        wait for 50 ns;
        -- 167
        wait for 50 ns;
        -- 168
        wait for 50 ns;
        -- 169
        wait for 50 ns;
        -- 170
        wait for 50 ns;
        -- 171
        wait for 50 ns;
        -- 172
        wait for 50 ns;
        -- 173
        wait for 50 ns;
        -- 174
        wait for 50 ns;
        -- 175
        wait for 50 ns;
        -- 176
        wait for 50 ns;
        -- 177
        wait for 50 ns;
        -- 178
        wait for 50 ns;
        -- 179
        wait for 50 ns;
        -- 180
        wait for 50 ns;
        -- 181
        wait for 50 ns;
        -- 182
        wait for 50 ns;
        -- 183
        wait for 50 ns;
        -- 184
        wait for 50 ns;
        -- 185
        wait for 50 ns;
        -- 186
        wait for 50 ns;
        -- 187
        wait for 50 ns;
        -- 188
        wait for 50 ns;
        -- 189
        wait for 50 ns;
        -- 190
        wait for 50 ns;
        -- 191
        wait for 50 ns;
        -- 192
        wait for 50 ns;
        -- 193
        wait for 50 ns;
        -- 194
        wait for 50 ns;
        -- 195
        wait for 50 ns;
        -- 196
        wait for 50 ns;
        -- 197
        wait for 50 ns;
        -- 198
        wait for 50 ns;
        -- 199
        wait for 50 ns;
        -- 200
        wait for 50 ns;
        -- 201
        wait for 50 ns;
        -- 202
        wait for 50 ns;
        -- 203
        wait for 50 ns;
        -- 204
        wait for 50 ns;
        -- 205
        wait for 50 ns;
        -- 206
        wait for 50 ns;
        -- 207
        wait for 50 ns;
        -- 208
        wait for 50 ns;
        -- 209
        wait for 50 ns;
        -- 210
        wait for 50 ns;
        -- 211
        wait for 50 ns;
        -- 212
        wait for 50 ns;
        -- 213
        wait for 50 ns;
        -- 214
        wait for 50 ns;
        -- 215
        wait for 50 ns;
        -- 216
        wait for 50 ns;
        -- 217
        wait for 50 ns;
        -- 218
        wait for 50 ns;
        -- 219
        wait for 50 ns;
        -- 220
        wait for 50 ns;
        -- 221
        wait for 50 ns;
        -- 222
        wait for 50 ns;
        -- 223
        wait for 50 ns;
        -- 224
        wait for 50 ns;
        -- 225
        wait for 50 ns;
        -- 226
        wait for 50 ns;
        -- 227
        wait for 50 ns;
        -- 228
        wait for 50 ns;
        -- 229
        wait for 50 ns;
        -- 230
        wait for 50 ns;
        -- 231
        wait for 50 ns;
        -- 232
        wait for 50 ns;
        -- 233
        wait for 50 ns;
        -- 234
        wait for 50 ns;
        -- 235
        wait for 50 ns;
        -- 236
        wait for 50 ns;
        -- 237
        wait for 50 ns;
        -- 238
        wait for 50 ns;
        -- 239
        wait for 50 ns;
        -- 240
        wait for 50 ns;
        -- 241
        wait for 50 ns;
        -- 242
        wait for 50 ns;
        -- 243
        wait for 50 ns;
        -- 244
        wait for 50 ns;
        -- 245
        wait for 50 ns;
        -- 246
        wait for 50 ns;
        -- 247
        wait for 50 ns;
        -- 248
        wait for 50 ns;
        -- 249
        wait for 50 ns;
        -- 250
        wait for 50 ns;
        -- 251
        wait for 50 ns;
        -- 252
        wait for 50 ns;
        -- 253
        wait for 50 ns;
        -- 254
        wait for 50 ns;
    end process;
end behave;
