#include "IntegerArray.h"
#include <sstream>

// g++ -shared -o libIntegerArray.dylib -fPIC IntegerArray.cpp

// Method to add an integer to the array
void IntegerArray::add(int value) {
    arr.push_back(value);
}

// Method to get the state of the array as a string
std::string IntegerArray::getState() {
    std::stringstream ss;
    ss << "[";
    for (size_t i = 0; i < arr.size(); ++i) {
        ss << arr[i];
        if (i != arr.size() - 1) {
            ss << ", ";
        }
    }
    ss << "]";
    return ss.str();
}

// C-style function to create a new IntegerArray instance
extern "C" {
    IntegerArray* IntegerArray_new() {
        return new IntegerArray();
    }

    // C-style function to add an integer to the array
    void IntegerArray_add(IntegerArray* obj, int value) {
        obj->add(value);
    }

    // C-style function to get the state of the array
    const char* IntegerArray_getState(IntegerArray* obj) {
        static std::string state = obj->getState();  // Use static to ensure it persists
        return state.c_str();  // Return pointer to static string
    }

    // C-style function to delete the IntegerArray object
    void IntegerArray_delete(IntegerArray* obj) {
        delete obj;
    }
}
