#include "mainwindow.h"
#include "ui_mainwindow.h"
#include "myudp.h"

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    //QHostAddress addr=QHostAddress::LocalHost;
    //ui->statusBar->showMessage(addr.toString());
    ui->lineEdit->setFocusPolicy(Qt::StrongFocus);
    ui->textBrowser->setFocusPolicy(Qt::NoFocus);

    QString Octet = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])";
    ui->IPlineEdit->setValidator(new QRegExpValidator(
    QRegExp("^" + Octet + "\\." + Octet + "\\." + Octet + "\\." + Octet + "$"), this));

    ui->targetPortEdit->setValidator(new QIntValidator(0, 65535, this));
    ui->listenPortEdit->setValidator(new QIntValidator(0, 65535, this));

    ui->IPlineEdit->setText("192.168.10.1");
    ui->targetPortEdit->setText("1234");
    ui->listenPortEdit->setText("1234");
    ui->lineEdit->setFocus();

    senderAddr.setAddress(ui->IPlineEdit->text());
    senderPort=ui->targetPortEdit->text().toInt();

    tableFormat.setBorder(0);

    connect(ui->pushButton,SIGNAL(clicked()),this,SLOT(sendMessage()));
    connect(ui->lineEdit,SIGNAL(returnPressed()),this,SLOT(sendMessage()));
    connect(ui->IPlineEdit,SIGNAL(textChanged(QString)),this,SLOT(enableUpdateButton()));
    connect(ui->targetPortEdit,SIGNAL(textChanged(QString)),this,SLOT(enableUpdateButton()));
    connect(ui->listenPortEdit,SIGNAL(textChanged(QString)),this,SLOT(enableUpdateButton()));

    connect(ui->updateButton,SIGNAL(clicked()),this,SLOT(updateConfig()));

    myudp=new MyUDP;
    connect(myudp,SIGNAL(newMessage(QString,QString)),this,SLOT(appendMessage(QString,QString)));
    connect(myudp,SIGNAL(bindSuccess(bool)),this,SLOT(udpBinded(bool)));
    myudp->bindPort(ui->listenPortEdit->text().toInt());
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::appendMessage(const QString &from, const QString &message)
{
    if (from.isEmpty() || message.isEmpty())
        return;

    QTextCursor cursor(ui->textBrowser->textCursor());
    cursor.movePosition(QTextCursor::End);

    QTextTable *table = cursor.insertTable(1, 2, tableFormat);
    table->cellAt(0, 0).firstCursorPosition().insertText('<' + from + "> ");
    table->cellAt(0, 1).firstCursorPosition().insertText(message);
    QScrollBar *bar = ui->textBrowser->verticalScrollBar();
    bar->setValue(bar->maximum());
}

void MainWindow::sendMessage()
{
    QString text = ui->lineEdit->text();
    if (text.isEmpty())
        return;

    if (text.startsWith(QChar('/'))) {
        QColor color = ui->textBrowser->textColor();
        ui->textBrowser->setTextColor(Qt::red);
        ui->textBrowser->append(tr("! Unknown command: %1")
                                .arg(text.left(text.indexOf(' '))));
        ui->textBrowser->setTextColor(color);
    } else {
        myudp->sendMessage(senderAddr,senderPort,text);
        appendMessage("client", text);
        //myudp->sendMessage(text);
    }

    ui->lineEdit->clear();
}

void MainWindow::udpBinded(bool isBinded)
{
    ui->updateButton->setDisabled(isBinded);
}

void MainWindow::enableUpdateButton()
{
    ui->updateButton->setDisabled(false);
}

void MainWindow::updateConfig()
{
    disconnect(this,SLOT(appendMessage(QString,QString)));
    disconnect(this,SLOT(udpBinded(bool)));
    senderAddr.setAddress(ui->IPlineEdit->text());
    senderPort=ui->targetPortEdit->text().toInt();
    myudp->unBind();
    delete myudp;
    myudp=new MyUDP;
    connect(myudp,SIGNAL(newMessage(QString,QString)),this,SLOT(appendMessage(QString,QString)));
    connect(myudp,SIGNAL(bindSuccess(bool)),this,SLOT(udpBinded(bool)));
    myudp->bindPort(ui->listenPortEdit->text().toInt());
}
