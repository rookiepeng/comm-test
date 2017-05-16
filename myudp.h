#ifndef MYUDP_H
#define MYUDP_H

#include <QUdpSocket>

class MyUDP: public QUdpSocket
{
    Q_OBJECT
public:
    MyUDP(QObject *parent = 0);

signals:
    void newMessage(const QString &from, const QString &message);

public slots:
    void readyRead();
    void sendMessage(QString string);

private:
    QUdpSocket *socket;

};

#endif // MYUDP_H
