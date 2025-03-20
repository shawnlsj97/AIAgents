package main

import "C"

// Compile into a shared library: go build -o golib.so -buildmode=c-shared golib.go

//export HelloGo
func HelloGo() *C.char {
	return C.CString("Hello from Go")
}

func main() {}
