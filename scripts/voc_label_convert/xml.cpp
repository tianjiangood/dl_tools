#include "xml.h"
#include "libxml/xmlwriter.h"
#include "libxml/tree.h"


void XMLWrite(const char* xmlPath, Annotation & annotation){
	xmlDocPtr doc = NULL;
	xmlNodePtr root_node = NULL, node = NULL, objectNode = NULL, node1 = NULL;
	//Creates a new document, a node and set it as a root node
	doc = xmlNewDoc(BAD_CAST "1.0");
	root_node = xmlNewNode(NULL, BAD_CAST "annotation");
	//xmlNewProp(root_node, BAD_CAST "version", BAD_CAST "1.0");
	xmlDocSetRootElement(doc, root_node);

	//creates a new node, which is "attached" as child node of root_node node.
	xmlNewChild(root_node, NULL, BAD_CAST "folder", BAD_CAST annotation.folder.c_str());
	xmlNewChild(root_node, NULL, BAD_CAST "filename", BAD_CAST annotation.filename.c_str());

	node = xmlNewChild(root_node, NULL, BAD_CAST "source", NULL);
	xmlNewChild(node, NULL, BAD_CAST "database", BAD_CAST annotation.source.database.c_str());
	xmlNewChild(node, NULL, BAD_CAST "annotation", BAD_CAST annotation.source.annotation.c_str());
	xmlNewChild(node, NULL, BAD_CAST "image", BAD_CAST annotation.source.image.c_str());
	xmlNewChild(node, NULL, BAD_CAST "flickrid", BAD_CAST annotation.source.flickrid.c_str());

	node = xmlNewChild(root_node, NULL, BAD_CAST "owner", NULL);
	xmlNewChild(node, NULL, BAD_CAST "flickrid", BAD_CAST annotation.owner.flickrid.c_str());
	xmlNewChild(node, NULL, BAD_CAST "name", BAD_CAST annotation.owner.name.c_str());

	node = xmlNewChild(root_node, NULL, BAD_CAST "size", NULL);
	char temp[32];
	_itoa(annotation.size.width, temp, 10);
	xmlNewChild(node, NULL, BAD_CAST "width", BAD_CAST _itoa(annotation.size.width, temp, 10));
	xmlNewChild(node, NULL, BAD_CAST "height", BAD_CAST _itoa(annotation.size.height, temp, 10));
	xmlNewChild(node, NULL, BAD_CAST "depth", BAD_CAST _itoa(annotation.size.depth, temp, 10));

	xmlNewChild(root_node, NULL, BAD_CAST "segmented", BAD_CAST annotation.segmented.c_str());

	for (int i = 0; i < annotation.objectList.size(); i++){
		objectNode = xmlNewChild(root_node, NULL, BAD_CAST "object", NULL);
		xmlNewChild(objectNode, NULL, BAD_CAST "name", BAD_CAST annotation.objectList[i].name.c_str());
		xmlNewChild(objectNode, NULL, BAD_CAST "pose", BAD_CAST annotation.objectList[i].pose.c_str());
		xmlNewChild(objectNode, NULL, BAD_CAST "truncated", BAD_CAST annotation.objectList[i].truncated.c_str());
		xmlNewChild(objectNode, NULL, BAD_CAST "difficult", BAD_CAST annotation.objectList[i].difficult.c_str());
		node = xmlNewChild(objectNode, NULL, BAD_CAST "bndbox", NULL);
		xmlNewChild(node, NULL, BAD_CAST "xmin", BAD_CAST _itoa(annotation.objectList[i].bndbox.xmin, temp, 10));
		xmlNewChild(node, NULL, BAD_CAST "ymin", BAD_CAST _itoa(annotation.objectList[i].bndbox.ymin, temp, 10));
		xmlNewChild(node, NULL, BAD_CAST "xmax", BAD_CAST _itoa(annotation.objectList[i].bndbox.xmax, temp, 10));
		xmlNewChild(node, NULL, BAD_CAST "ymax", BAD_CAST _itoa(annotation.objectList[i].bndbox.ymax, temp, 10));
	}

	//// xmlNewProp() creates attributes, which is "attached" to an node.
	//node = xmlNewChild(root_node, NULL, BAD_CAST "node3", BAD_CAST"node has attributes");
	//xmlNewProp(node, BAD_CAST "attribute", BAD_CAST "yes");
	////Here goes another way to create nodes.
	//node = xmlNewNode(NULL, BAD_CAST "node4");
	//node1 = xmlNewText(BAD_CAST"other way to create content");
	//xmlAddChild(node, node1);
	//xmlAddChild(root_node, node);

	xmlSaveFormatFileEnc(xmlPath, doc, "UTF-8", 1);//Dumping document to stdio or file
	xmlFreeDoc(doc);
	xmlCleanupParser();
	xmlMemoryDump();//debug memory for regression tests
}


void XMLRead(const char* xmlPath, Annotation & annotation){
	xmlDocPtr doc;
	xmlNodePtr curNode;
	xmlChar *szKey;
	string filename = "";
	doc = xmlReadFile(xmlPath, "UTF-8", XML_PARSE_RECOVER); //解析文件"GB2312"
	if (doc == NULL){
		fprintf(stderr, "Document not parsed successfully.\n");
	}
	curNode = xmlDocGetRootElement(doc); //确定文档根元素
	if (NULL == curNode){
		fprintf(stderr, "empty document\n");
		xmlFreeDoc(doc);
	}
	if (xmlStrcmp(curNode->name, BAD_CAST "annotation")) {
		fprintf(stderr, "document of the wrong type, root node != Message");
		xmlFreeDoc(doc);
	}

	curNode = curNode->xmlChildrenNode;
	xmlNodePtr propNodePtr = curNode;
	xmlNodePtr sourceNodePtr = NULL;
	xmlNodePtr ownerNodePtr = NULL;
	xmlNodePtr sizeNodePtr = NULL;
	xmlNodePtr objectNodePtr = NULL;
	vector<xmlNodePtr> objectListP;
	xmlNodePtr objectNodePtr2 = NULL;
	xmlNodePtr bndboxNodePtr = NULL;

	// annotation
	while (curNode != NULL){
		//取出文件名称
		if (!xmlStrcmp(curNode->name, BAD_CAST "folder")) {
			annotation.folder = (char*)xmlNodeGetContent(curNode);
		}
		if (!xmlStrcmp(curNode->name, BAD_CAST "filename")) {
			annotation.filename = (char*)xmlNodeGetContent(curNode);
		}
		if (!xmlStrcmp(curNode->name, BAD_CAST "source")) {
			sourceNodePtr = curNode->xmlChildrenNode;
		}
		if (!xmlStrcmp(curNode->name, BAD_CAST "owner")) {
			ownerNodePtr = curNode->xmlChildrenNode;
		}
		if (!xmlStrcmp(curNode->name, BAD_CAST "size")) {
			sizeNodePtr = curNode->xmlChildrenNode;
		}
		if (!xmlStrcmp(curNode->name, BAD_CAST "segmented")) {
			annotation.segmented = (char*)xmlNodeGetContent(curNode);
		}
		if (!xmlStrcmp(curNode->name, BAD_CAST "object")) {
			objectNodePtr = curNode->xmlChildrenNode;
			objectListP.push_back(objectNodePtr);
		}
		curNode = curNode->next;
	}
	// source
	while (sourceNodePtr != NULL){
		if (!xmlStrcmp(sourceNodePtr->name, BAD_CAST "database")) {
			annotation.source.database = (char*)xmlNodeGetContent(sourceNodePtr);
		}
		if (!xmlStrcmp(sourceNodePtr->name, BAD_CAST "annotation")) {
			annotation.source.annotation = (char*)xmlNodeGetContent(sourceNodePtr);
		}
		if (!xmlStrcmp(sourceNodePtr->name, BAD_CAST "image")) {
			annotation.source.image = (char*)xmlNodeGetContent(sourceNodePtr);
		}
		if (!xmlStrcmp(sourceNodePtr->name, BAD_CAST "flickrid")) {
			annotation.source.flickrid = (char*)xmlNodeGetContent(sourceNodePtr);
		}
		sourceNodePtr = sourceNodePtr->next;
	}
	// owner
	while (ownerNodePtr != NULL){
		if (!xmlStrcmp(ownerNodePtr->name, BAD_CAST "flickrid")) {
			annotation.owner.flickrid = (char*)xmlNodeGetContent(ownerNodePtr);
		}
		if (!xmlStrcmp(ownerNodePtr->name, BAD_CAST "name")) {
			annotation.owner.name = (char*)xmlNodeGetContent(ownerNodePtr);
		}
		ownerNodePtr = ownerNodePtr->next;
	}
	// size
	while (sizeNodePtr != NULL){
		if (!xmlStrcmp(sizeNodePtr->name, BAD_CAST "width")) {
			annotation.size.width = atoi((char*)xmlNodeGetContent(sizeNodePtr));
		}
		if (!xmlStrcmp(sizeNodePtr->name, BAD_CAST "height")) {
			annotation.size.height = atoi((char*)xmlNodeGetContent(sizeNodePtr));
		}
		if (!xmlStrcmp(sizeNodePtr->name, BAD_CAST "depth")) {
			annotation.size.depth = atoi((char*)xmlNodeGetContent(sizeNodePtr));
		}
		sizeNodePtr = sizeNodePtr->next;
	}
	// object
	for (int i = 0; i < objectListP.size(); i++){
		objectNodePtr = objectListP[i];
		while (objectNodePtr != NULL)
		{
			if (!xmlStrcmp(objectNodePtr->name, BAD_CAST "name")) {
				annotation.object.name = (char*)xmlNodeGetContent(objectNodePtr);
			}
			if (!xmlStrcmp(objectNodePtr->name, BAD_CAST "pose")) {
				annotation.object.pose = (char*)xmlNodeGetContent(objectNodePtr);
			}
			if (!xmlStrcmp(objectNodePtr->name, BAD_CAST "truncated")) {
				annotation.object.truncated = (char*)xmlNodeGetContent(objectNodePtr);
			}
			if (!xmlStrcmp(objectNodePtr->name, BAD_CAST "difficult")) {
				annotation.object.difficult = (char*)xmlNodeGetContent(objectNodePtr);
			}
			if (!xmlStrcmp(objectNodePtr->name, BAD_CAST "bndbox")) {
				bndboxNodePtr = objectNodePtr->xmlChildrenNode;
			}
			objectNodePtr = objectNodePtr->next;
		}
		// bndbox
		while (bndboxNodePtr != NULL){
			if (!xmlStrcmp(bndboxNodePtr->name, BAD_CAST "xmin")) {
				annotation.object.bndbox.xmin = atoi((char*)xmlNodeGetContent(bndboxNodePtr));
			}
			if (!xmlStrcmp(bndboxNodePtr->name, BAD_CAST "ymin")) {
				annotation.object.bndbox.ymin = atoi((char*)xmlNodeGetContent(bndboxNodePtr));
			}
			if (!xmlStrcmp(bndboxNodePtr->name, BAD_CAST "xmax")) {
				annotation.object.bndbox.xmax = atoi((char*)xmlNodeGetContent(bndboxNodePtr));
			}
			if (!xmlStrcmp(bndboxNodePtr->name, BAD_CAST "ymax")) {
				annotation.object.bndbox.ymax = atoi((char*)xmlNodeGetContent(bndboxNodePtr));
			}
			bndboxNodePtr = bndboxNodePtr->next;
		}
		annotation.objectList.push_back(annotation.object);
	}
	xmlFreeDoc(doc);
}
