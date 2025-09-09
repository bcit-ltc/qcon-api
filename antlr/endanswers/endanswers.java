import org.antlr.v4.runtime.*;

import org.antlr.v4.runtime.tree.*;

import java.io.OutputStream;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerException;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import org.w3c.dom.Attr;
import org.w3c.dom.Document;
import org.w3c.dom.Element;

import java.io.File; // Import the File class
import java.io.IOException; // Import this class to handle errors

import java.nio.file.*;

import java.io.InputStreamReader;
import java.io.BufferedReader;
import java.lang.StringBuilder;

public class endanswers {

    public static DocumentBuilderFactory documentFactory;
    public static DocumentBuilder documentBuilder;
    public static Document document;
    public static Element root;

    public static class endanswersVisitor extends
            endanswersBaseVisitor<Void> {

        public Void visitAnswer(endanswersParser.AnswerContext ctx) {
            // Read Answer if present
            try {
                ctx.NUMLIST_PREFIX().getText();
                ctx.answer_content().getText();

                // System.out.println(ctx.NUMLIST_PREFIX().getText());
                // System.out.println(ctx.answer_content().getText());

                Element answer = document.createElement("answer");

                Element index = document.createElement("index");
                index.appendChild(document.createTextNode(ctx.NUMLIST_PREFIX().getText()));
                answer.appendChild(index);

                Element content = document.createElement("content");
                content.appendChild(document.createTextNode(ctx.answer_content().getText()));
                answer.appendChild(content);

                root.appendChild(answer);

            } catch (Exception e) {
            }

            return null;
        }

    }

    public static void serializeDocument(Document document, OutputStream os) {
        try {
            TransformerFactory tFactory = TransformerFactory.newInstance();
            Transformer transformer = tFactory.newTransformer();
            transformer.setOutputProperty(OutputKeys.INDENT, "yes");

            DOMSource source = new DOMSource(document);
            StreamResult result = new StreamResult(os);
            transformer.transform(source, result);
        } catch (TransformerException e) {
            e.printStackTrace();
        }
    }

    public static void printDocument(Document document) {
        serializeDocument(document, System.out);
    }

    public static String readinput() {
        InputStreamReader reader = new InputStreamReader(System.in);
        char[] buffer = new char[1000];
        StringBuilder sb = new StringBuilder();
        String input = "";
        int count;
        try {
            while ((count = reader.read(buffer)) != -1) {
                sb.append(buffer, 0, count);
            }
            input = sb.toString();
        } catch (Exception e) {
            e.printStackTrace();
        }
        return input;
    }

    public static void main(String args[]) {

        String Content = null;

        if (args.length == 0) {
            Content = readinput();
        } else {
            try {
                Path fileName = Paths.get(args[0]);
                Content = Files.readString(fileName);
            } catch (IOException e) {
                System.out.println("endanswers error reading file:" + args[0]);
                e.printStackTrace();
            }
        }

        endanswersLexer questionparserLexer = new endanswersLexer(CharStreams.fromString(Content));
        CommonTokenStream tokens = new CommonTokenStream(questionparserLexer);
        endanswersParser parser = new endanswersParser(tokens);

        ParseTree tree = parser.endanswers();

        try {
            documentFactory = DocumentBuilderFactory.newInstance();
            documentBuilder = documentFactory.newDocumentBuilder();
            document = documentBuilder.newDocument();
            root = document.createElement("root");
            document.appendChild(root);
        } catch (ParserConfigurationException pce) {
            pce.printStackTrace();
        }

        endanswersVisitor loader = new endanswersVisitor();
        loader.visit(tree);
        printDocument(document);
    }
}