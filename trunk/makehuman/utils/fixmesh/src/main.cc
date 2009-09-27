/*
	main.cc
	Thomas Larsson 2009
	thomas_larsson_01@hotmail.com

	Main program
*/

#include "stdafx.h"
#include <error.h>
#include "hdr.h"

/*
	Global variables
*/

char theDir[BUFSIZE];
int verbosity;
double weightStep;
double zoneSize;
double detailThreshold;
bool allocGroups;
bool stripPrefix;

/*
	FILE *fileOpen(const char *fileName, const char *mode)

 	fopen in theDir, throws an error if cannot open.
*/

FILE *fileOpen(const char *fileName, const char *mode)
{
	char buf[BUFSIZE];
	sprintf(buf, "%s%s", theDir, fileName);
	FILE *fp = fopen(buf, mode);
	if (fp == 0)
		RaiseError1("Could not open %s\n", buf);
	return fp;
}

/*
	Error handling.

 	Primitive but works.
*/

char theError[BUFSIZE];
void raiseError()
{
//	printf("errno = %d 0x%x\n", errno, errno);
	printf("ERROR: %s\n", theError);
	fflush(stdin);
	getchar();
	exit(-1);
}


/*
 Main
 */		

int main(int argc, char* argv[])
{
	enum {
		M_BUILD,
		M_CONVERT,
		M_GROUP,
		M_VIEW
	} mode;

	Mesh mesh1, mesh2;
	char name1[BUFSIZE];
	char name2[BUFSIZE];
	char grName2[BUFSIZE];
	char morph[BUFSIZE];
	char moName1[BUFSIZE];
	char moName2[BUFSIZE];
	memset(morph, 0, BUFSIZE*sizeof(char));

	int group;
	double threshold;

	// Default values for global variables
	bool objFile = false;
	bool detail = false;
	verbosity = 2;
	zoneSize = 2.0;
	weightStep = 0.2;
	detailThreshold = 0.7;
	
	// default names, for debugging

//	strcpy(morph, "data/old/targets/macrodetails/africa-aethiopid-female-child.target");
//	strcpy(morph, "data/old/targets/microdetails/head-back-skull-scale-depth-decr.target");
	strcpy(morph, "data/old/targets/details/ear-trans-in.target");
	strcpy(theDir, "/home/thomas/fixmesh/");

	
	// parse command line

	mode = M_GROUP;

	int i = 0;
	while (++i < argc) {
		if (strcmp(argv[i], "-verbosity") == 0) {
			if (sscanf(argv[++i], "%d", &verbosity) != 1) goto parseError;
		}
		else if (strcmp(argv[i], "-weight") == 0) {
			if (sscanf(argv[++i], "%lf", &weightStep) != 1) goto parseError;
		}
		else if (strcmp(argv[i], "-zone") == 0) {
			if (sscanf(argv[++i], "%lf", &zoneSize) != 1) goto parseError;
		}
		else if (strcmp(argv[i], "-build") == 0) 
			mode = M_BUILD;
		else if (strcmp(argv[i], "-group") == 0) 
			mode = M_GROUP;
		else if (strcmp(argv[i], "-obj") == 0) 
			objFile = true;
		else if (strcmp(argv[i], "-detail") == 0) {
			detail = true;
			if (sscanf(argv[++i], "%lf", &detailThreshold) != 1) goto parseError;
		}
		else if (strcmp(argv[i], "-convert") == 0) {
			mode = M_CONVERT;
			i += 1;
			if (sscanf(argv[i], "%s", morph) != 1) goto parseError;
		}
		else if (strcmp(argv[i], "-view") == 0) {
			mode = M_VIEW;
			i += 1;
			if (sscanf(argv[i], "%s", morph) != 1) goto parseError;
		}
		else if (strcmp(argv[i], "-dir") == 0) {
			i += 1;
			if (sscanf(argv[i], "%s", theDir) != 1) goto parseError;
		}
		else
			goto parseError;
	}

	// Define the file names.
	
	
	sprintf(moName1, "data/old/targets/%s", morph+17);
	sprintf(moName2, "data/new/targets/%s", morph+17);

	if (verbosity > 0)
		printf("%s\n ->  %s\n", moName1, moName2);
//	return 0;

	// Run the program

	switch(mode) {

	case M_BUILD:
		// Build mode: create the table that maps the meshes.
		sprintf(name1, "base/old/base-mat");
		sprintf(name2, "base/new/base-mat");
		printf("Building table %s -> %s\n", name1, name2);

		mesh1.readObjFile (name1, F_ONLYTRIS);
		mesh1.findCenter();
		mesh1.m_center.dump(stdout, "Center ", "\n");
		dumpMesh(&mesh1, name1);

		mesh2.readObjFile (name2, F_ONLYTRIS);
		mesh2.findCenter();
		mesh2.m_center.dump(stdout, "Center ", "\n");
		dumpMesh(&mesh2, name2);

		mesh1.remapMaterials (&mesh2);

		storeWeights("wtable.txt", &mesh1, &mesh2);
		printf("Table %s -> %s built\n", name1, name2);
		break;

	case M_GROUP:
		// Build mode: create the table that maps the meshes.
		sprintf(name1, "base/old/base");
		sprintf(name2, "base/new/base-mat");
		sprintf(grName2, "base/new/grbase");
		stripPrefix = false;

		mesh1.readObjFile (name1, F_ONLYTRIS | F_ALLOCGROUPS | F_TEXTVERTS);
		mesh2.readObjFile (name2, 0);
		mesh2.readWeights("wtable.txt");
		mesh2.findGroups(&mesh1);
//		mesh2.findTextVerts(&mesh1);

		mesh2.writeObjFile(name2, 0, grName2, F_MHX );
//		mesh1.saveGroups("g1table.txt");
//		mesh2.saveGroups("g2table.txt");
		if (verbosity > 0)
			printf("%s grouped\n", grName2);
		break;

	case M_CONVERT:
		// Convert mode: convert a morph. Need old morph, new base
		// mesh, and the conversion table.
		sprintf(name1, "base/old/base-mat");
		sprintf(name2, "base/new/base-mat");
		if (verbosity > 0)
			printf("Converting %s -> %s\n", moName1, moName2);
		
		mesh1.readObjFile (name1, F_ALLOCGROUPS | F_ONLYTRIS);
		mesh1.readTargetFile (moName1, threshold);
		dumpMesh(&mesh1, moName1);

		mesh2.readObjFile (name2, 0);
		mesh2.readWeights("wtable.txt");
		mesh2.moveWeights(&mesh1);	

		if (objFile)
			mesh2.writeObjFile(name2, 0, moName2, F_MHX);

#if 0			
		if (detail) {
			mesh1.readGroups("g1table.txt");
			mesh2.readGroups("g2table.txt");
			group = mesh2.groupFromName(morph+30);
		}
		else 
			group = -1;
#endif
		mesh2.writeTargetFile(moName2, detail, 0.5*threshold);
		if (verbosity > 0)
			printf("%s -> %s converted\n", moName1, moName2);
		break;

	case M_VIEW:
		// View mode for debugging: create an obj file from a
		// target file.
		sprintf(name1, "base/old/base-mat");
		printf("Making %s viewable obj file\n", moName1);
		mesh1.readObjFile (name1, 0);
		mesh1.readTargetFile (moName1, threshold);
		mesh1.writeObjFile(name1, 0, moName1, 0);
		printf("Viewable obj file %s made\n", moName1);
		break;
	}

	printf("Done\n");
	fflush(stdin);
//	getchar();
	return 0;

parseError:
	printf("Error when parsing command line\n");
	printf("Usage:\n");
	printf("-build\n");
	printf("-group\n");
	printf("-convert morph\n");
	printf("-view morph\n");
	printf("-verbosity level\n");
	printf("-weight W\n");
	printf("-zone Z\n");
	printf("-dir directory\n");
	printf("-obj\n");
	printf("-detail\n");
}
