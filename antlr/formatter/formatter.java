import org.antlr.v4.runtime.tree.ParseTreeWalker;
import org.antlr.v4.misc.OrderedHashMap;
import org.antlr.v4.runtime.*;

import org.antlr.v4.runtime.tree.*;

import java.util.Map;
import java.util.*;

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
public class formatter {

   public static DocumentBuilderFactory documentFactory;
   public static DocumentBuilder documentBuilder;
   public static Document document;
   public static Element root;

   public static class formatterVisitor extends
         formatterBaseVisitor<Void> {

      public Void visitMaincontent_title(formatterParser.Maincontent_titleContext ctx){
         Element unused_content = document.createElement("maincontent_title");
         unused_content.appendChild(document.createTextNode(ctx.getText()));
         root.appendChild(unused_content);
         return null;
      }

      // public Void visitSectioninfo(formatterParser.SectioninfoContext ctx){
      //    Element sectioninfo = document.createElement("sectioninfo");
      //    sectioninfo.appendChild(document.createTextNode(ctx.getText()));
      //    root.appendChild(sectioninfo);
      //    return null;
      // }

      public Void visitBody(formatterParser.BodyContext ctx) {
         Element body = document.createElement("body");
         body.appendChild(document.createTextNode(ctx.getText()));
         root.appendChild(body);
         return null;
      }

      public Void visitEnd_answers(formatterParser.End_answersContext ctx) {
         Element end_answers = document.createElement("end_answers");
         end_answers.appendChild(document.createTextNode(ctx.getText()));
         root.appendChild(end_answers);
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

   public static String readinput(){
      InputStreamReader reader = new InputStreamReader(System.in);

      char[] buffer = new char[1000];
      StringBuilder sb = new StringBuilder();
      String input = "";
      int count;           
      try{
         while((count = reader.read(buffer)) != -1) {
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

      // String pandocContent = readinput();

      formatterLexer formatterLexer = new formatterLexer(CharStreams.fromString(Content));
      CommonTokenStream tokens = new CommonTokenStream(formatterLexer);
      formatterParser parser = new formatterParser(tokens);

      ParseTree tree = parser.formatter();

      try {
         documentFactory = DocumentBuilderFactory.newInstance();
         documentBuilder = documentFactory.newDocumentBuilder();
         document = documentBuilder.newDocument();
         root = document.createElement("root");
         document.appendChild(root);
      } catch (ParserConfigurationException pce) {
         pce.printStackTrace();
      }

      formatterVisitor loader = new formatterVisitor();
      loader.visit(tree);

      printDocument(document);

      // try {
      // // transform the DOM Object to an XML File
      // String targetfile = args[0] + "formatter.xml";

      // TransformerFactory transformerFactory = TransformerFactory.newInstance();
      // Transformer transformer = transformerFactory.newTransformer();
      // DOMSource domSource = new DOMSource(document);
      // StreamResult streamResult = new StreamResult(new File(targetfile));
      // transformer.transform(domSource, streamResult);
      // } catch (TransformerException tfe) {
      // System.out.println("formatter error writing: " + args[0]);
      // tfe.printStackTrace();
      // }

   }

}