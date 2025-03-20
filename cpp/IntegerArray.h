#ifndef INTEGER_ARRAY_H
#define INTEGER_ARRAY_H

#include <string>
#include <vector>

class IntegerArray {
private:
    std::vector<int> arr;

public:
    // Method to add an integer to the array
    void add(int value);

    // Method to get the state of the array as a string
    std::string getState();
};

// Exposing C-style functions to interact with the class
extern "C" {
    IntegerArray* IntegerArray_new();
    void IntegerArray_add(IntegerArray* obj, int value);
    const char* IntegerArray_getState(IntegerArray* obj);
    void IntegerArray_delete(IntegerArray* obj);
}

#endif // INTEGER_ARRAY_H
