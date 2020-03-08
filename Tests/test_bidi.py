from collections import deque
import pytest
from fontgoggles.misc.bidi import applyBiDi, getBiDiInfo, detectScript, textSegments


testData = [
    ("Abc", "Abc",
     {'base_dir': 'L',
      'base_level': 0,
      'chars': [{'ch': 'A',
                 'index': 0,
                 'level': 0,
                 'orig': 'L',
                 'type': 'L'},
                {'ch': 'b',
                 'index': 1,
                 'level': 0,
                 'orig': 'L',
                 'type': 'L'},
                {'ch': 'c',
                 'index': 2,
                 'level': 0,
                 'orig': 'L',
                 'type': 'L'}],
      'runs': deque([{'eor': 'L',
                      'length': 3,
                      'sor': 'L',
                      'start': 0,
                      'type': 'L'}])}),
    ("\u062D\u062A\u0649", "\u0649\u062A\u062D",
     {'base_dir': 'R',
      'base_level': 1,
      'chars': [{'ch': '\u0649',
                 'index': 2,
                 'level': 1,
                 'orig': 'AL',
                 'type': 'R'},
                {'ch': '\u062A',
                 'index': 1,
                 'level': 1,
                 'orig': 'AL',
                 'type': 'R'},
                {'ch': '\u062D',
                 'index': 0,
                 'level': 1,
                 'orig': 'AL',
                 'type': 'R'}],
      'runs': deque([{'eor': 'R',
                      'length': 3,
                      'sor': 'R',
                      'start': 0,
                      'type': 'AL'}])}),
    ("\u062D\u062A\u064912", "12\u0649\u062A\u062D",
     {'base_dir': 'R',
      'base_level': 1,
      'chars': [{'ch': '1',
                 'index': 3,
                 'level': 2,
                 'orig': 'EN',
                 'type': 'AN'},
                {'ch': '2',
                 'index': 4,
                 'level': 2,
                 'orig': 'EN',
                 'type': 'AN'},
                {'ch': '\u0649',
                 'index': 2,
                 'level': 1,
                 'orig': 'AL',
                 'type': 'R'},
                {'ch': '\u062A',
                 'index': 1,
                 'level': 1,
                 'orig': 'AL',
                 'type': 'R'},
                {'ch': '\u062D',
                 'index': 0,
                 'level': 1,
                 'orig': 'AL',
                 'type': 'R'}],
      'runs': deque([{'eor': 'R',
                      'length': 5,
                      'sor': 'R',
                      'start': 0,
                      'type': 'EN'}])}),
    ("\u0627\u064f\u0633", "\u0633\u0627\u064f",
     {'base_dir': 'R',
      'base_level': 1,
      'chars': [{'ch': 'س',
                 'index': 2,
                 'level': 1,
                 'orig': 'AL',
                 'type': 'R'},
                {'ch': 'ا',
                 'index': 0,
                 'level': 1,
                 'orig': 'AL',
                 'type': 'R'},
                {'ch': 'ُ',
                 'index': 1,
                 'level': 1,
                 'orig': 'NSM',
                 'type': 'R'}],
      'runs': deque([{'eor': 'R',
                      'length': 3,
                      'sor': 'R',
                      'start': 0,
                      'type': 'AL'}])}),
]


@pytest.mark.parametrize("testString,expectedString,expectedInfo", testData)
def test_getBiDiInfo_ltr(testString, expectedString, expectedInfo):
    info, display = getBiDiInfo(testString)
    assert display == expectedString
    assert info == expectedInfo


testDataApplyBiDi = [
    ("Abc", "Abc", [3], "L",
     [0, 1, 2], [0, 1, 2]),
    ("\u062D\u062A\u064912", "12\u0649\u062A\u062D", [2, 3], "R",
     [4, 3, 2, 0, 1], [3, 4, 2, 1, 0]),
]


@pytest.mark.parametrize("testString,expectedString,expectedRunLengths,expectedDir,expectedToBiDi,expectedFromBiDi",
                         testDataApplyBiDi)
def test_applyBiDi(testString, expectedString, expectedRunLengths, expectedDir, expectedToBiDi, expectedFromBiDi):
    display, runLenghts, baseDirection, toBiDi, fromBiDi = applyBiDi(testString)
    assert display == expectedString
    assert runLenghts == expectedRunLengths
    assert baseDirection == expectedDir
    assert toBiDi == expectedToBiDi
    assert fromBiDi == expectedFromBiDi
    assert set(toBiDi) == set(range(len(toBiDi)))
    assert set(toBiDi) == set(fromBiDi)


testDataDetectScript = [
    (" ", ['Zxxx']),
    ("abc", ['Latn', 'Latn', 'Latn']),
    ("(abc)", ['Latn', 'Latn', 'Latn', 'Latn', 'Latn']),
    ("\u0627\u064f\u0633", ['Arab', 'Arab', 'Arab']),
    ("(\u0627\u064f\u0633)", ['Arab', 'Arab', 'Arab', 'Arab', 'Arab']),
    ("a(\u0627\u064f\u0633)", ['Latn', 'Latn', 'Arab', 'Arab', 'Arab', 'Arab']),
    ("a(\u0627\u064f\u0633)a", ['Latn', 'Latn', 'Arab', 'Arab', 'Arab', 'Latn', 'Latn']),
    ("\u0627\u064f(a)\u0633", ['Arab', 'Arab', 'Arab', 'Latn', 'Arab', 'Arab']),
]


@pytest.mark.parametrize("testString,expectedScripts", testDataDetectScript)
def test_detectScript(testString, expectedScripts):
    assert detectScript(testString) == expectedScripts


testDataTextSegments = [
    ("a", 0, [("a", "Latn", 0)]),
    ("\u0627", 1, [("\u0627", "Arab", 1)]),
    ("a\u0627", 0, [("a", "Latn", 0), ("\u0627", "Arab", 1)]),
    ("\u0627123", 1, [("\u0627", "Arab", 1), ("123", "Arab", 2)]),
    ("\u0627123\u0627", 1, [("\u0627", "Arab", 1), ("123", "Arab", 2), ("\u0627", "Arab", 1)]),
    ("123\u0627", 1, [("123", "Arab", 2), ("\u0627", "Arab", 1)]),
    ("a123\u0627", 0, [("a123", "Latn", 0), ("\u0627", "Arab", 1)]),
]


@pytest.mark.parametrize("testString,expectedBaseLevel,expectedSegments", testDataTextSegments)
def test_textSegments(testString, expectedBaseLevel, expectedSegments):
    segments, baseLevel = textSegments(testString)
    assert baseLevel == expectedBaseLevel
    assert len(segments) == len(expectedSegments)
    for segment, expectedSegment in zip(segments, expectedSegments):
        assert segment == expectedSegment
