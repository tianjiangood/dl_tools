#ifndef _xml_H__
#define _xml_H__


#include <stdio.h>
#include <string>
#include <iostream>
#include <vector>

using namespace std;
typedef struct _Source {
	string database;
	string annotation;
	string image;
	string flickrid;
} Source, *PSource;

typedef struct _Owner {
	string flickrid;
	string name;
} Owner, *POwner;

typedef struct _Size {
	int width;
	int height;
	int depth;
} Size, *PSize;

typedef struct _RECT {
	int xmin;
	int ymin;
	int xmax;
	int ymax;
} RECT, *PRECT;

typedef struct _Object {
	string name;
	string pose;
	string truncated;
	string difficult;
	RECT  bndbox;
} Object, *PObject;

class Annotation
{
public:
	string folder;
	string filename;
	Source source;
	Owner owner;
	Size size;
	string segmented;
	vector<Object> objectList;
	Object object;
	Annotation() { 

		folder=string("INRIA_PERSON");
		filename = string("png");

		source.database = string("INRIA_PERSON");
		source.annotation = string("INRIA_PERSON");
		source.flickrid = string("00000");
		source.image = string("flick");

		owner.flickrid = string("00000");
		owner.name = string("inria");

		segmented = string("0");
	};
	virtual ~Annotation() {};
};

///< 
void XMLRead(const char* xmlPath, Annotation & annotation);
///<
void XMLWrite(const char* xmlPath, Annotation & annotation);


#endif // _xml_H__

