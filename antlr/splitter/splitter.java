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

public class splitter {

   public static DocumentBuilderFactory documentFactory;
   public static DocumentBuilder documentBuilder;
   public static Document document;
   public static Element root;

   public static class splitterVisitor extends
         splitterBaseVisitor<Void> {
      public Void visitSplitter(splitterParser.SplitterContext ctx) {

         int numberofquestions = ctx.questions().size();

         // CHECK IF FIRST QUESTION WAS FOUND
         try {
            Element question = document.createElement("question");
            question.setAttribute("id", Integer.toString(0));
              
            try {
               Element content = document.createElement("content");
               content.appendChild(document.createTextNode(ctx.first_question().content().getText()));
               question.appendChild(content);
               root.appendChild(question);
            } catch (Exception e) {
            }

         } catch (Exception e) {
         }

         for (int i = 0; i < numberofquestions; i++) {
            Element question = document.createElement("question");
            question.setAttribute("id", Integer.toString(i + 1));

            try {
               Element content = document.createElement("content");
               content.appendChild(document.createTextNode(ctx.questions().get(i).getText()));
               question.appendChild(content);

            } catch (Exception e) {
            }

            root.appendChild(question);
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
            System.out.println("splitter error reading file:" + args[0]);
            e.printStackTrace();
         }
      }

      splitterLexer splitterLexer = new splitterLexer(CharStreams.fromString(Content));
      CommonTokenStream tokens = new CommonTokenStream(splitterLexer);
      splitterParser parser = new splitterParser(tokens);

      ParseTree tree = parser.splitter();

      try {
         documentFactory = DocumentBuilderFactory.newInstance();
         documentBuilder = documentFactory.newDocumentBuilder();
         document = documentBuilder.newDocument();
         root = document.createElement("root");
         document.appendChild(root);
      } catch (ParserConfigurationException pce) {
         pce.printStackTrace();
      }

      splitterVisitor loader = new splitterVisitor();
      loader.visit(tree);

      printDocument(document);

   }
}