#include <iostream>
#include <string>
using namespace std;
class Car {
public:
    string brand; 
    string color;
    Car(string b, string c) {
        brand = b;
        color = c;
    }
    void startEngine() {
        cout << brand << " গাড়ির ইঞ্জিন চালু হয়েছে!" << endl;
    }
};
int main() {
    Car myCar("Toyota", "লাল");
    
    cout << "গাড়ির ব্র্যান্ড: " << myCar.brand << endl;
    cout << "গাড়ির রং: " << myCar.color << endl;

    myCar.startEngine();

    return 0;
}
