// # This Source Code Form is subject to the terms of the Mozilla Public # License, v. 2.0. If a
// copy of the MPL was not distributed with this # file, You can obtain one at
// https://mozilla.org/MPL/2.0/.

grammar sectioner;

sectioner: section+ EOF;

section:
	SECTION_START title? sectiontext? sectioncontent SECTION_END 
	| maincontent;

title: HEADING;

sectiontext: 
	ALL_CHARACTER+;

sectioncontent:
	QUESTION_HEADER? QUESTION_PREFIX ALL_CHARACTER+
	| sectioncontent QUESTION_HEADER? QUESTION_PREFIX ALL_CHARACTER+;

maincontent: 
	QUESTION_HEADER? QUESTION_PREFIX ALL_CHARACTER+
	| maincontent QUESTION_HEADER? QUESTION_PREFIX ALL_CHARACTER+;

// ================================ TOKENS
fragment NEWLINE: ('\r'? '\n' | '\r');
fragment WHITESPACE: ' ' | '\t';
fragment DIGIT: [0-9];
fragment NUMBER: DIGIT+ (DIGIT+)?;
fragment CLOSING_PARENTHESIS: ')';
fragment BACKSLASH: '\\';
fragment DOT: '.';
fragment ASTERISK: '*';
fragment DOUBLE_ASTERISK: '**';
fragment DELIMITER: BACKSLASH? (DOT | CLOSING_PARENTHESIS);
fragment GREATER_THAN: '>';
fragment COLON:   ':';
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

fragment HASH: '#';
fragment DOUBLE_HASH: '##';

fragment HEADING_START: (HASH | DOUBLE_HASH) WHITESPACE;
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

QUESTION_PREFIX:
	NEWLINE WHITESPACE* DOUBLE_ASTERISK? NUMBER WHITESPACE* DELIMITER WHITESPACE*;

SECTION_START:
	NEWLINE ((HASH | DOUBLE_HASH)? WHITESPACE)? (ASTERISK|DOUBLE_ASTERISK)? HASH S E C T I O N WHITESPACE* (ASTERISK|DOUBLE_ASTERISK)? NEWLINE NEWLINE_ADDED*;
SECTION_END:
	NEWLINE ((HASH | DOUBLE_HASH)? WHITESPACE)? (ASTERISK|DOUBLE_ASTERISK)? '/' S E C T I O N WHITESPACE* (ASTERISK|DOUBLE_ASTERISK)? NEWLINE NEWLINE_ADDED*; 

HEADING: NEWLINE HEADING_START (~'#' | ~'\n') .*? NEWLINE;

ALL_CHARACTER: .;
