// # This Source Code Form is subject to the terms of the Mozilla Public # License, v. 2.0. If a
// copy of the MPL was not distributed with this # file, You can obtain one at
// https://mozilla.org/MPL/2.0/.

grammar questionparser;

// questionparser: unused_content? question_header? question_wrapper hint? answers? wr_answer? EOF;

questionparser:
	unused_content? question_header? question_wrapper wr_answer? EOF;

unused_content: content;

question_header: question_header_part+;

question_header_part:
	TITLE content
	| POINTS content
	| TYPE content
	| RANDOMIZE content;

// question_wrapper: NUMLIST_PREFIX content feedback? (anylist_item)* feedback? hint? anylist_item*;
// anylist_item: (LETTERLIST_PREFIX|CORRECT_ANSWER|NUMLIST_PREFIX) content feedback?;

question_wrapper: object*;
object: (LETTERLIST_PREFIX|CORRECT_ANSWER|NUMLIST_PREFIX|HINT|FEEDBACK) content;

// letterlist: (LETTERLIST_PREFIX_A|CORRECT_ANSWER_A) (content|NUMLIST_PREFIX content)+ feedback? letterlist_item+;
// letterlist_item:
// 		(LETTERLIST_PREFIX|CORRECT_ANSWER) (content|NUMLIST_PREFIX content)+ feedback?;

// numlist_item: NUMLIST_PREFIX content;

// question_part: content NUMLIST_PREFIX question_part | content NUMLIST_PREFIX question_part |
// content NUMLIST_PREFIX | content;

// letterlist: (letterlist_part | correct_answer_part)+; letterlist_part: LETTERLIST_PREFIX
// feedback? content feedback?; correct_answer_part: CORRECT_ANSWER feedback? content feedback?;
wr_answer: CORRECT_ANSWER_FOR_WR wr_answer_content;

wr_answer_content: (content|object*) object*;

// hint: HINT content;
// feedback: FEEDBACK content;
content: ALL_CHARACTER+;

// ================================ TOKENS
fragment DIGIT: [0-9];
fragment NEWLINE: ('\r'? '\n' | '\r');
fragment CLOSING_PARENTHESIS: ')';
fragment LETTER: [a-zA-Z];
fragment NUMBER: DIGIT+ (DIGIT+)?;
fragment BACKSLASH: '\\';
fragment ASTERISK: '*';
fragment DOUBLE_ASTERISK: '**';
fragment DOT: '.';
fragment WHITESPACE: ' ' | '\t';
fragment DELIMITER: BACKSLASH? (DOT | CLOSING_PARENTHESIS);
fragment ANSWER_MARKER: BACKSLASH ASTERISK;
fragment COLON: ':';
fragment A: 'A' | 'a';
fragment B: 'B' | 'b';
fragment C: 'C' | 'c';
fragment D: 'D' | 'd';
fragment E: 'E' | 'e';
fragment F: 'F' | 'f';
fragment H: 'H' | 'h';
fragment I: 'I' | 'i';
fragment K: 'K' | 'k';
fragment L: 'L' | 'l';
fragment M: 'M' | 'm';
fragment N: 'N' | 'n';
fragment O: 'O' | 'o';
fragment P: 'P' | 'p';
fragment R: 'R' | 'r';
fragment S: 'S' | 's';
fragment T: 'T' | 't';
fragment U: 'U' | 'u';
fragment W: 'W' | 'w';
fragment Y: 'Y' | 'y';
fragment Z: 'Z' | 'z';
fragment OPEN_BRACKET: '\\[';
fragment CLOSE_BRACKET: '\\]';
fragment AT: '@';
fragment ONE: '1';

// fragment STAR_AFTER_DELIMITER_A:
// 	NEWLINE WHITESPACE* A WHITESPACE* DELIMITER WHITESPACE* ANSWER_MARKER WHITESPACE*;
// fragment STAR_BEFORE_DELIMITER_A:
// 	NEWLINE WHITESPACE* A WHITESPACE* ANSWER_MARKER WHITESPACE* DELIMITER WHITESPACE*;
// fragment STAR_BEFORE_LETTER_A:
// 	NEWLINE WHITESPACE* ANSWER_MARKER WHITESPACE* A WHITESPACE* DELIMITER WHITESPACE*;

fragment STAR_AFTER_DELIMITER:
	NEWLINE WHITESPACE* LETTER WHITESPACE* DELIMITER WHITESPACE* ANSWER_MARKER WHITESPACE*;
fragment STAR_BEFORE_DELIMITER:
	NEWLINE WHITESPACE* LETTER WHITESPACE* ANSWER_MARKER WHITESPACE* DELIMITER WHITESPACE*;
fragment STAR_BEFORE_LETTER:
	NEWLINE WHITESPACE* ANSWER_MARKER WHITESPACE* LETTER WHITESPACE* DELIMITER WHITESPACE*;

fragment TITLE_KEYWORD:
	NEWLINE WHITESPACE* T I T L E S? WHITESPACE* COLON;
fragment POINTS_KEYWORD:
	NEWLINE WHITESPACE* P O I N T S? WHITESPACE* COLON;
fragment TYPE_KEYWORD:
	NEWLINE WHITESPACE* T Y P E S? WHITESPACE* COLON;
fragment RANDOMIZE_KEYWORD:
	NEWLINE WHITESPACE* R A N D O M (I Z E)? (S | D)? WHITESPACE* COLON;

TITLE: TITLE_KEYWORD;
POINTS: POINTS_KEYWORD;
TYPE: TYPE_KEYWORD;
RANDOMIZE: RANDOMIZE_KEYWORD;

// NUMLIST_PREFIX_1:
// 	NEWLINE WHITESPACE* DOUBLE_ASTERISK? ONE WHITESPACE* DELIMITER WHITESPACE*;

NUMLIST_PREFIX:
	NEWLINE WHITESPACE* DOUBLE_ASTERISK? NUMBER WHITESPACE* DELIMITER WHITESPACE*;

// LETTERLIST_PREFIX_A:
// 	NEWLINE WHITESPACE* A WHITESPACE* DELIMITER WHITESPACE*;

LETTERLIST_PREFIX:
	NEWLINE WHITESPACE* LETTER WHITESPACE* DELIMITER WHITESPACE*;

FEEDBACK:
	NEWLINE WHITESPACE* (ASTERISK | DOUBLE_ASTERISK)? AT F E E D B A C K COLON? WHITESPACE*;
HINT:
	NEWLINE WHITESPACE* (ASTERISK | DOUBLE_ASTERISK)? AT H I N T COLON? WHITESPACE*;

// CORRECT_ANSWER_A: (
// 		STAR_AFTER_DELIMITER_A
// 		| STAR_BEFORE_DELIMITER_A
// 		| STAR_BEFORE_LETTER_A
// 	);

CORRECT_ANSWER: (
		STAR_AFTER_DELIMITER
		| STAR_BEFORE_DELIMITER
		| STAR_BEFORE_LETTER
	);

CORRECT_ANSWER_FOR_WR:
	NEWLINE WHITESPACE* C O R R E C T WHITESPACE* A N S W E R S? WHITESPACE* COLON WHITESPACE*;

ALL_CHARACTER: .;