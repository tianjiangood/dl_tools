#include <iostream>
#include <sstream>
#include <fstream>
#include <string>
#include <io.h>
#include "xml.h"


using namespace std;
#pragma comment(lib,"libxml2.lib")


#ifndef MAX 
#define MAX(a,b) ((a)>(b)?(a):(b))
#endif 

#ifndef MIN 
#define MIN(a,b) ((a)<(b)?(a):(b))
#endif 



string *label_string = NULL;

//解析标签文件,输出到ann中
static int parse_dat( char* filename,Annotation& ann )
{
	std::ifstream fin( filename, std::ios::in );
	char line[1024]={0};
	int w,h,c;
	int x0,x1,y0,y1,nr;
	int label;
	int counter = 0;

	while(fin.getline(line, sizeof(line)))
	{
		if( line[0]=='#' ) continue;

		if(counter==0)
		{
			ann.filename = string(line);
		}
		else if(counter==1)
		{
			sscanf( line,"%dx%dx%d",&w,&h,&c);
			ann.size.depth = c;
			ann.size.width = w;
			ann.size.height = h;
		}
		else if(counter==2)
		{
			sscanf( line,"%dx",&nr);
		}
		else
		{
			Object obj;
			
			sscanf(line, "%d,%d,%d,%d,%d", &label,&x0, &y0, &x1, &y1);
			obj.bndbox.xmin = MAX(1,x0);
			obj.bndbox.ymin = MAX(1,y0);
			obj.bndbox.xmax = MIN(w-1,x1);
			obj.bndbox.ymax = MIN(h-1,y1);

			if ( (obj.bndbox.xmax - obj.bndbox.xmin)<5 ||
				(obj.bndbox.ymax - obj.bndbox.ymin)<5 ) 
			{
				printf("111111\n");
			}

			obj.truncated = string("0");
			obj.difficult = string("0");
			obj.name = label_string[label];
			obj.pose = string("front");
			ann.objectList.push_back(obj);
			ann.object = obj;
		}
		counter++;
	}

	fin.clear();
	fin.close();
	return (counter>2);
}

 //遍历path目录下的下的标签文件，解析出来并保存为xml格式
static void dir( string path,char* save_path )
{
	long hFile = 0;
	struct _finddata_t fileInfo;
	string pathName, exdName;
	int counter = 0;

	// \\* 代表要遍历所有的类型
	if ((hFile = _findfirst(pathName.assign(path).append("\\*").c_str(), &fileInfo)) == -1)
	{
		return;
	}

	do 
	{
		Annotation annotation;  
		char dat_file[260];
		char save_file[260];
		char tmp_fn[260];
		//判断文件的属性是文件夹还是文件
		if( fileInfo.attrib&_A_SUBDIR ) continue;

		strcpy( tmp_fn,fileInfo.name );
		tmp_fn[strlen(tmp_fn)-4]= 0;

		sprintf( dat_file,"%s//%s", path.c_str(), fileInfo.name );
		sprintf( save_file,"%s//%s.xml",save_path, tmp_fn );

		if (counter>0 && (counter % 1000) == 0)
		{
			printf("pasred file number :%d\n", counter);
		}

		parse_dat(dat_file,annotation);

		XMLWrite(save_file, annotation);  

		counter++;

	} while (_findnext(hFile, &fileInfo) == 0);
	_findclose(hFile);

	printf("finished pasred file number :%d\n", counter);

	return;
}

static void print_help( char* proc_name )
{
	printf("%s from_path to_path label_name\n", proc_name);
	printf("from_path:origin annotations diretctoy.\n");
	printf("to_path:voc foramt annotations save to where.\n");
	printf("label_name:label name file.splited by space" " \n");
	getchar();
}


int main( int argc, char** argv )
{  
	//label标签
	string label_string_def[] = { string("background"), string("person") };

	//label文件目录
	char src_path[] = "F:/data/Pedestrian/VOCCaltechPed/Ann_dat/";

	//xml文件输出目录
	char dst_path[] = "F:/data/Pedestrian/VOCCaltechPed/Annotations/";
	
	//运行
	label_string = label_string_def;
	dir( string(src_path),dst_path );

	return 0;  
} 