//SET DA TELA TOUCH SCREEN
#include <SoftwareSerial.h>

#define rx_pin 2
#define tx_pin 3

SoftwareSerial my_serial(rx_pin, tx_pin);

//VARIÁVEIS PARA CONTROLE DOS DADOS DO POTENCIÔMETRO
const int potentiometer = 0;
int value;
int lowestValue;
int greaterValue;

//SET DO BOTÃO
int button = 7;
bool run = false;
int play = 10;

//SET DOS ENDEREÇOS DA TELA
unsigned char writePotentiometer[16] = {0x5A, 0xA5, 0x0D, 0x82, 0x03, 0x10, 0x5A, 0xA5, 0x01, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00};
unsigned char writeCurrentValue[8] = {0x5A, 0xA5, 0x05, 0x82, 0x10, 0x00, 0x00, 0x00};
unsigned char writeGreaterValue[8] = {0x5A, 0xA5, 0x05, 0x82, 0x30, 0x00, 0x00, 0x00};
unsigned char writeLowestValue[8] = {0x5A, 0xA5, 0x05, 0x82, 0x20, 0x00, 0x00, 0x00};
unsigned char clearGraphic[8] = {0x5A, 0xA5, 0x05, 0x82, 0x03, 0x01, 0x00, 0x00};

//VARIÁVEIS PARA O USO DO MILLIS
unsigned long startMillis = 0;
unsigned long currentMillis = 0;

void setup() {
  //START DOS COMPONENTES NECESSÁRIOS
  Serial.begin(9600);
  my_serial.begin(9600);

  pinMode(button, INPUT_PULLUP);

  delay(2000);
}

void loop() {
  //VERIFICAÇÃO DO BOTÃO
  if (digitalRead(button) == LOW) {
    run = true;
    Serial.println("1");
    startMillis = millis();
  }

  if (Serial.available() > 0) {
    char dado = Serial.read();

    if (dado == '1') {
      run = true;
      startMillis = millis();
    }
  }

  //LOOP PRINCIPAL
  while (run == true) {
    //LIMPANDO A TELA
    my_serial.write(clearGraphic, sizeof(clearGraphic));

    currentMillis = 0;
    lowestValue = 1023;
    greaterValue = 0;

    //LOOP QUE INFORMA OS VALORES (2min DE DURAÇÃO)
    while (currentMillis < 120000) {
      //ATT DO TEMPO E ADIÇÃO DO POTENCIÔMETRO
      currentMillis = millis() - startMillis;
      value = analogRead(potentiometer);

      //ENVIO SERIAL QUE É COLOETADO EM PYTHON
      Serial.write((value >> 8) & 0xFF);
      Serial.write(value & 0xFF);

      //LIMPANDO OS DADOS DAS POSIÇÕES ESPECÍFICAS DO GRÁFICO
      writeCurrentValue[12] = 0x00;
      writeCurrentValue[13] = 0x00;
      writeCurrentValue[14] = 0x00;
      writeCurrentValue[15] = 0x00;
      my_serial.write(writePotentiometer, sizeof(writePotentiometer));

      //ESCREVENDO O VALOR NO GRÁFICO
      writePotentiometer[12] = highByte(value);
      writePotentiometer[13] = lowByte(value);

      writePotentiometer[14] = highByte(value);
      writePotentiometer[15] = lowByte(value);
      my_serial.write(writePotentiometer, sizeof(writePotentiometer));

      //ESCREVENDO O VALOR ATUAL NA SUA ÁREA DE INFORMAÇÃO
      writeCurrentValue[6] = highByte(value);
      writeCurrentValue[7] = lowByte(value);
      my_serial.write(writeCurrentValue, sizeof(writeCurrentValue));
      
      //VERIFICAÇÃO E ATT DO MENOR VALOR APRESENTADO NO GRÁFICO
      if (value < lowestValue) {
        lowestValue = value;
      }

      //VERIFICAÇÃO E ATT DO MAIOR VALOR APRESENTADO NO GRÁFICO
      if (value > greaterValue) {
        greaterValue = value;
      }

      //ESCREVENDO O MENOR E O MAIOR VALOR NAS SUAS RESPECTIVAS ÁREAS DE INFORMAÇÃO
      writeLowestValue[6] = highByte(lowestValue);
      writeLowestValue[7] = lowByte(lowestValue);
      my_serial.write(writeLowestValue, sizeof(writeLowestValue));

      writeGreaterValue[6] = highByte(greaterValue);
      writeGreaterValue[7] = lowByte(greaterValue);
      my_serial.write(writeGreaterValue, sizeof(writeGreaterValue));

      //TEMPO DE ATUALIZAÇÃO DAS INFORMAÇÕES 264
      delay(429);
    }
    //APÓS OS 2MIN FINALIZA O LOOP PRINCIPAL
    run = false;
  }
}