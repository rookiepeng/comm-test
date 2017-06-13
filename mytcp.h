#ifndef MYTCP_H
#define MYTCP_H

#include <QTcpSocket>

class MyTCP : public QTcpSocket
{
    Q_OBJECT
public:
    explicit MyTCP(QObject *parent = nullptr);
    void doConnect();

signals:

public slots:
    void connected();
    void disconnected();
    void bytesWritten(qint64 bytes);
    void readyRead();

private:
    QTcpSocket *tcpSocket;
};

#endif // MYTCP_H
