"""Compile/run selected portable C snippets from the tutorial against tiny stubs.

This catches syntax errors and the original bxCAN send/decoder pitfalls without
pretending to cross-compile the vendor HAL or test the physical CAN bus.
"""
import html
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def snippet(chapter: str, index: int) -> str:
    text = (ROOT / (chapter + ".html")).read_text(encoding="utf-8")
    blocks = re.findall(r"<pre><code>(.*?)</code></pre>", text, re.S)
    return html.unescape(blocks[index])


@unittest.skipUnless(shutil.which("gcc"), "gcc unavailable")
class TestPortableCExamples(unittest.TestCase):
    def compile_and_run(self, source: str) -> None:
        with tempfile.TemporaryDirectory() as d:
            cfile = Path(d) / "test.c"
            binary = Path(d) / "test"
            cfile.write_text(source, encoding="utf-8")
            subprocess.run(
                ["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                 str(cfile), "-o", str(binary)],
                check=True, capture_output=True, text=True,
            )
            subprocess.run([str(binary)], check=True,
                           capture_output=True, text=True)

    def test_chapter_10_spl_send(self):
        # Chapter 10 was updated to CAN_SendStandard and added a vendor header
        # after this portable regression test was written. Keep testing both
        # chapter versions against the same tiny SPL stubs, without a HAL SDK.
        fragment = snippet("10", 0)
        fragment = "\n".join(
            line for line in fragment.splitlines()
            if line.strip() != '#include "stm32f10x_can.h"'
        )
        function_name = (
            "CAN_SendStandard" if "CAN_SendStandard(" in fragment else "CAN_SendStd"
        )
        source = r"""
#include <stdint.h>
#include <stddef.h>
#include <assert.h>
#define CAN1 1
#define CAN_Id_Standard 0
#define CAN_RTR_Data 0
#define CAN_TxStatus_NoMailBox 4
typedef struct {
    uint32_t StdId, IDE, RTR, DLC;
    uint8_t Data[8];
} CanTxMsg;
static CanTxMsg last;
static int sent = 0;
static uint8_t CAN_Transmit(int can, CanTxMsg *msg) {
    assert(can == CAN1);
    last = *msg;
    ++sent;
    return 0;
}
""" + fragment + r"""
int main(void) {
    uint8_t payload[3] = {0x10, 0x20, 0x30};
    assert(CAN_SendStd(0x321, payload, 3) == 0);
    assert(sent == 1);
    assert(last.StdId == 0x321 && last.IDE == 0 && last.RTR == 0);
    assert(last.DLC == 3);
    assert(last.Data[0] == 0x10 && last.Data[2] == 0x30);
    assert(last.Data[7] == 0);
    assert(CAN_SendStd(0x800, payload, 3) == CAN_TxStatus_NoMailBox);
    assert(CAN_SendStd(0x321, payload, 9) == CAN_TxStatus_NoMailBox);
    assert(CAN_SendStd(0x321, NULL, 1) == CAN_TxStatus_NoMailBox);
    assert(sent == 1);
    return 0;
}
"""
        self.compile_and_run(source.replace("CAN_SendStd(", function_name + "("))

    def test_chapter_27_signal_decode(self):
        source = r"""
#include <stdint.h>
#include <stddef.h>
#include <assert.h>
""" + snippet("27", 0) + "\n" + snippet("27", 1) + r"""
int main(void) {
    CanFrame_t frame = {0};
    frame.id = 0x100;
    frame.dlc = 3;
    frame.data[1] = 0xB8;
    frame.data[2] = 0x0B;
    float v = Protocol_GetVehicleSpeed(&frame);
    assert(v > 29.99f && v < 30.01f);
    frame.dlc = 2;
    assert(Protocol_GetVehicleSpeed(&frame) == -1.0f);
    frame.dlc = 3;
    frame.is_ext = 1;
    assert(Protocol_GetVehicleSpeed(&frame) == -1.0f);
    return 0;
}
"""
        self.compile_and_run(source)


if __name__ == "__main__":
    unittest.main()
