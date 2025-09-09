// # This Source Code Form is subject to the terms of the Mozilla Public
// # License, v. 2.0. If a copy of the MPL was not distributed with this
// # file, You can obtain one at https://mozilla.org/MPL/2.0/.

grammar endanswers;

endanswers: unused_content? answer+ EOF;

unused_content: ALL_CHARACTER+;

answer: NUMLIST_PREFIX answer_content?;

answer_content: ALL_CHARACTER+;
// ================================ TOKENS
fragment NEWLINE:   ('\r'? '\n' | '\r');
fragment CLOSING_PARENTHESIS: ')';
fragment BACKSLASH: '\\';
fragment ASTERISK: '*';
fragment DOUBLE_ASTERISK: '**';
fragment DOT: '.';
fragment WHITESPACE: ' ' | '\t';
fragment DELIMITER: BACKSLASH? (DOT | CLOSING_PARENTHESIS);
fragment GREATER_THAN: '>';
fragment COLON:   ':';
fragment DIGIT: [0-9];
fragment NUMBER: DIGIT*;

NUMLIST_PREFIX: NEWLINE WHITESPACE* GREATER_THAN? WHITESPACE* DOUBLE_ASTERISK? NUMBER WHITESPACE* WHITESPACE* DELIMITER WHITESPACE*;

ALL_CHARACTER: .;