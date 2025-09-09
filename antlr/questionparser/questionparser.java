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

public class questionparser {

   public static DocumentBuilderFactory documentFactory;
   public static DocumentBuilder documentBuilder;
   public static Document document;
   public static Element root;

   public static class questionparserVisitor extends
         questionparserBaseVisitor<Void> {

      public Void visitQuestion_header_part(questionparserParser.Question_header_partContext ctx) {
         // Read Title if present
         try {
            ctx.TITLE().getText();
            Element title = document.createElement("title");
            title.appendChild(document.createTextNode(ctx.content().getText()));
            root.appendChild(title);
         } catch (Exception e) {
         }
         // Read Points if present
         try {
            ctx.POINTS().getText();
            Element points = document.createElement("points");
            points.appendChild(document.createTextNode(ctx.content().getText()));
            root.appendChild(points);
         } catch (Exception e) {
         }
         // Read Type if present
         try {
            ctx.TYPE().getText();
            Element type = document.createElement("type");
            type.appendChild(document.createTextNode(ctx.content().getText()));
            root.appendChild(type);
         } catch (Exception e) {
         }
         // Read Randomize if present
         try {
            ctx.RANDOMIZE().getText();
            Element randomize = document.createElement("randomize");
            randomize.appendChild(document.createTextNode(ctx.content().getText()));
            root.appendChild(randomize);
         } catch (Exception e) {
         }
         return null;
      }

      public Void visitQuestion_wrapper(questionparserParser.Question_wrapperContext ctx) {
         
         int NumberofObjects = ctx.object().size();
         Element question_body = document.createElement("question_body");

         for (int i = 0; i < NumberofObjects; i++) {
            Element question_body_part = document.createElement("question_body_part");
            Element prefix = document.createElement("prefix");
            Element content = document.createElement("content");
            
            // Add NUMLIST_PREFIX
            try{
               prefix.appendChild(document.createTextNode(ctx.object().get(i).NUMLIST_PREFIX().getText()));
               question_body_part.setAttribute("prefix_type", "NUMLIST_PREFIX");
            } catch (Exception e) {
            }

            // Add LETTERLIST_PREFIX
            try{
               prefix.appendChild(document.createTextNode(ctx.object().get(i).LETTERLIST_PREFIX().getText()));
               question_body_part.setAttribute("prefix_type", "LETTERLIST_PREFIX");
            } catch (Exception e) {
            }

            // Add CORRECT_ANSWER
            try{
               prefix.appendChild(document.createTextNode(ctx.object().get(i).CORRECT_ANSWER().getText()));
               question_body_part.setAttribute("prefix_type", "CORRECT_ANSWER");
            } catch (Exception e) {
            }

            // Add HINT
            try{
               prefix.appendChild(document.createTextNode(ctx.object().get(i).HINT().getText()));
               question_body_part.setAttribute("prefix_type", "HINT");
            } catch (Exception e) {
            }

            // Add FEEDBACK
            try{
               prefix.appendChild(document.createTextNode(ctx.object().get(i).FEEDBACK().getText()));
               question_body_part.setAttribute("prefix_type", "FEEDBACK");
            } catch (Exception e) {
            }

            // Add content
            try{
               // System.out.println(ctx.object().get(i).getText()); 
               content.appendChild(document.createTextNode(ctx.object().get(i).content().getText()));
            } catch (Exception e) {
            }

            question_body_part.appendChild(prefix);
            question_body_part.appendChild(content);
            question_body.appendChild(question_body_part);
         }
         root.appendChild(question_body);
         return null;
      }

      public Void visitWr_answer(questionparserParser.Wr_answerContext ctx) {
         try {
            Element content = document.createElement("content");
            String wr_answer_content = ctx.wr_answer_content().getText();            
            content.appendChild(document.createTextNode(wr_answer_content));
            Element wr_answer = document.createElement("wr_answer");
            wr_answer.appendChild(content);
            root.appendChild(wr_answer);
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
            System.out.println("questionparser error reading file:" + args[0]);
            e.printStackTrace();
         }
      }

      questionparserLexer questionparserLexer = new questionparserLexer(CharStreams.fromString(Content));
      CommonTokenStream tokens = new CommonTokenStream(questionparserLexer);
      questionparserParser parser = new questionparserParser(tokens);

      ParseTree tree = parser.questionparser();

      try {
         documentFactory = DocumentBuilderFactory.newInstance();
         documentBuilder = documentFactory.newDocumentBuilder();
         document = documentBuilder.newDocument();
         root = document.createElement("root");
         document.appendChild(root);
      } catch (ParserConfigurationException pce) {
         pce.printStackTrace();
      }

      questionparserVisitor loader = new questionparserVisitor();
      loader.visit(tree);
      printDocument(document);
   }
}