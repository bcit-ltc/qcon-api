// # This Source Code Form is subject to the terms of the Mozilla Public # License, v. 2.0. If a
// copy of the MPL was not distributed with this # file, You can obtain one at
// https://mozilla.org/MPL/2.0/.

grammar formatter;

formatter: maincontent_title? body end_answers? EOF;

maincontent_title: (ALL_CHARACTER+);

body:
    body (SECTION_START ALL_CHARACTER+)? QUESTION_HEADER? START_NUMBER_ONE ALL_CHARACTER+
    | body (SECTION_START ALL_CHARACTER+)? QUESTION_HEADER? ALL_CHARACTER+
    | (SECTION_START ALL_CHARACTER+)? QUESTION_HEADER? START_NUMBER_ONE ALL_CHARACTER+
    | (SECTION_START ALL_CHARACTER+)? QUESTION_HEADER? ALL_CHARACTER+;

end_answers: END_ANSWER_BLOCK ALL_CHARACTER+ START_NUMBER_ONE ALL_CHARACTER+;

// ================================ TOKENS
fragment NEWLINE: ('\r'? '\n' | '\r');
fragment CLOSING_PARENTHESIS: ')';
fragment BACKSLASH: '\\';
fragment ASTERISK: '*';
fragment DOUBLE_ASTERISK: '**';
fragment DOT: '.';
fragment GREATER_THAN: '>';
fragment COLON: ':';
fragment WHITESPACE: ' ' | '\t';
fragment DELIMITER: BACKSLASH? (DOT | CLOSING_PARENTHESIS);
fragment A:   'A' | 'a';
fragment B:   'B' | 'b';
fragment C:   'C' | 'c';
fragment D:   'D' | 'd';
fragment E:   'E' | 'e';
fragment F:   'F' | 'f';
fragment I:   'I' | 'i';
fragment K:   'K' | 'k';
fragment L:   'L' | 'l';
fragment M:   'M' | 'm';
fragment N:   'N' | 'n';
fragment O:   'O' | 'o';
fragment P:   'P' | 'p';
fragment R:   'R' | 'r';
fragment S:   'S' | 's';
fragment T:   'T' | 't';
fragment U:   'U' | 'u';
fragment W:   'W' | 'w';
fragment Y:   'Y' | 'y';  
fragment Z:   'Z' | 'z';  

fragment ANSWER: A N S W E R (S)?;

fragment HASH: '#';
fragment DOUBLE_HASH: '##';


fragment HEADING_START: NEWLINE (ASTERISK|DOUBLE_ASTERISK)? (HASH | DOUBLE_HASH) WHITESPACE;
fragment NEWLINE_ADDED: NEWLINE '<!-- NewLine -->' NEWLINE;

fragment TITLE:  NEWLINE WHITESPACE* GREATER_THAN? WHITESPACE* T I T L E S? WHITESPACE* COLON;
fragment POINTS:   NEWLINE WHITESPACE* GREATER_THAN? WHITESPACE* P O I N T S? WHITESPACE* COLON;
fragment TYPE:   NEWLINE WHITESPACE* GREATER_THAN? WHITESPACE* T Y P E S? WHITESPACE* COLON;
fragment RANDOMIZE:   NEWLINE WHITESPACE* GREATER_THAN? WHITESPACE* R A N D O M (I Z E)? (S | D)? WHITESPACE* COLON;

fragment QUESTION_HEADER_PARAMETER:
    POINTS ~[\n]+
    |   TITLE ~[\n]+
    |   TYPE ~[\n]+
    |   RANDOMIZE ~[\n]+;

fragment QUESTION_HEADER_WITH_NEWLINE_ADDED: (NEWLINE_ADDED? QUESTION_HEADER_PARAMETER NEWLINE_ADDED?)+;  
fragment QUESTION_HEADER_PART: QUESTION_HEADER_WITH_NEWLINE_ADDED;

QUESTION_HEADER: (QUESTION_HEADER_PART NEWLINE)+ NEWLINE_ADDED*;

SECTION_START:
	NEWLINE ((HASH | DOUBLE_HASH)? WHITESPACE)? (ASTERISK|DOUBLE_ASTERISK)? HASH S E C T I O N WHITESPACE* (ASTERISK|DOUBLE_ASTERISK)? NEWLINE+ HEADING_START?;


// START_OL: (NEWLINE WHITESPACE* '<!-- START OF OL -->') -> skip;
// END_OL: (NEWLINE WHITESPACE* '<!-- END OF OL -->') -> skip;
START_NUMBER_ONE: NEWLINE '1' WHITESPACE* DELIMITER;

END_ANSWER_BLOCK:
    NEWLINE WHITESPACE* ANSWER WHITESPACE* COLON WHITESPACE*;

ALL_CHARACTER: .;