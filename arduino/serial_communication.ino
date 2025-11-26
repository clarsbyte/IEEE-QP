void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
}

void loop() {
  String data;
  // put your main code here, to run repeatedly:
  if (Serial.available()){
    String data = Serial.readStringUntil('\n');  // Read until newline
    data.trim();  // Remove whitespace

    
    int commaIndex = data.indexOf(',');
    float ra = data.substring(0, commaIndex).toFloat();
    float dec = data.substring(commaIndex + 1).toFloat();

    Serial.println(ra);
    Serial.println(dec);

    delay(1000);
  }else{
    Serial.println("Moon");
  }
  
  delay(2000);
}
