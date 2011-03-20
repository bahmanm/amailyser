'''

@author: Bahman Movaqar
@contact: Bahman AT BahmanM.com
@copyright:  (c) Bahman Movaqar
@license: 
    This file is part of amailyser (The E-mail Analyser).

    amialyser is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    amialyser is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with amialyser.  If not, see <http://www.gnu.org/licenses/>.
    
@version: 0.0.1

'''

import mailbox, rfc822, datetime, time
import email.header as header
from model import Contact, Message, MsgRecipient
from model import session

###############################################################################
class MailBox:
    
    def __init__(self, path, boxtype='maildir'):
        self.path = path
        self.boxtype = boxtype
    
    ###########################     
    def open(self):
        if self.boxtype == 'maildir':
            self.box = mailbox.Maildir(self.path, create=False)
            self.box.lock()
        elif self.boxtype == 'mbox':
            self.box = mailbox.mbox(self.path, create=False)
            self.box.lock()
        else:
            raise Exception('Sorry but amailyzer does not support' 
                            + self.boxtype + 'mailbox type.')
    
    ###########################         
    def close(self):
        self.box.unlock()
        self.box.close()
    
    ###########################     
    def load(self, persist=True, echo=True):
        for m in self.box:
            mm = MailMessage(m)
            mm.process()
            if echo:
                print mm
            if persist:
                mm.persist()
    
    
###############################################################################
class MailMessage:
    
    def __init__(self, message):
        self.message = message
        self.messageid = ''
        self.inreplyto = ''
        self.size = 0
        self.cclist = []
        self.tolist = []
        self.subject = []
        self.msgfrom = {}
        self.date = None
        
    ###########################    
    def process(self):
        self.messageid = self.message['Message-ID']
        self.inreplyto = self.message['In-Reply-To']
        self.size = self._size(self.message)
        self.cclist = self._cc_list(self.message['Cc'])
        self.tolist = self._to_list(self.message['To'])
        self.subject = self._subject(self.message['Subject'])
        self.msgfrom = self._from(self.message['From'])
        self.date = self._date(self.message['Date'])
    
    ###########################
    def persist(self):
#        try:
        self._persist_contact(self.msgfrom)
        for item in self.tolist:
            self._persist_contact(item)
        for item in self.cclist:
            self._persist_contact(item)
        self._persist_recipients()
        self._persist_message()
        session.commit()
#        except:
#            print 'persist():  exception happened.'
#            pass
        
    ###########################
    def _persist_recipients(self):
        for item in self.tolist:
            r = MsgRecipient()
            (r.contact_email, r.recipient_type, r.message_id) = (item['email'], 'to', self.messageid)
            session.add(r)
        for item in self.cclist:
            r = MsgRecipient()
            (r.contact_email, r.recipient_type, r.message_id) = (item['email'], 'cc', self.messageid)
            session.add(r)
        #session.commit()
        
    ###########################
    def _persist_message(self):
        if session.query(Message).filter(Message.id == self.messageid).first():
            print 'Message with ID = (' + self.messageid + ') has already been persisted.  Skipping.'
            raise Exception()
        m = Message()
        m.id = self.messageid
        m.inreplyto = self.inreplyto
        m.fromcontact_email = self.msgfrom['email']
        m.size = self.size
        m.subject = self.subject
        m.msgdate = self.date
        session.add(m)
        #session.commit()
    
    ###########################
    def _persist_contact(self, contact):
        c = session.query(Contact).filter(Contact.email == contact['email']).first()
        if c == None:
            c = Contact()
            (c.email, c.name) = (contact['email'], contact['name'])
        session.add(c)
        #session.commit()
    
    ###########################
    def _size(self, message):
        size = 0
        if message.is_multipart():
            for p in message.get_payload():
                size += len(str(p))
        else:
            size = len(str(message.get_payload()))
        return size
    
    ###########################
    def _cc_list(self, ccfield):
        if ccfield == None:
            return []
        cclist = []
        ccitems = ccfield.split(',')
        for item in ccitems:
            if item == None:
                continue
            (name, email) = rfc822.parseaddr(item)
            if name == None and email == None:
                print 'Warning!  Could not parse ' + item + '.  Skipping.'
                continue
            [(text, charset)] = header.decode_header(name)
            name = unicode(text, charset or 'ascii')
            cclist.append({'name': name, 'email': email.lower()})
        return cclist
    
    ###########################
    def _to_list(self, tofield):
        if tofield == None:
            return []
        tolist = []
        toitems = tofield.split(',')
        for item in toitems:
            if item == None:
                continue
            (name, email) = rfc822.parseaddr(item)
            if name == None and email == None:
                print 'Warning!  Could not parse ' + item + '.  Skipping.'
                continue
            [(text, charset)] = header.decode_header(name)
            name = unicode(text, charset or 'ascii')
            tolist.append({'name': name, 'email': email.lower()})
        return tolist
    
    ###########################
    def _subject(self, subjectfield):
        [(text, charset)] = header.decode_header(subjectfield)
        return unicode(text, charset or 'ascii')
    
    ###########################
    def _from(self, fromfield):
        (name, email) = rfc822.parseaddr(fromfield)
        if name == None and email == None:
            print 'Warning!  Could not parse ' + fromfield + '.  Skipping.'
            return {}
        [(text, charset)] = header.decode_header(name)
        name = unicode(text, charset or 'ascii')
        return {'name': name, 'email': email.lower()}
    
    ###########################
    def _date(self, datefield):
        t = rfc822.parsedate(datefield)
        if t == None:
            print 'Warning!  Could not parse ' + str(datefield) + '.  Skipping.'
            return None
        return datetime.datetime.fromtimestamp(time.mktime(t))
        
    ###########################
    def __repr__(self):
        s = '{MailMessage  '
        s += '[Message-ID: ' + self.messageid + ']  '
        s += '[Subject: ' + self.subject + ']  '
        s += '[Date: ' + str(self.date) + ']  '
        s += '[From: ' + self.msgfrom['name'] + ' <' + self.msgfrom['email'] + '>]  '
        s += '[To: '
        for l in self.tolist:
            s += l['name'] + ' <' + l['email'] + '> '
        s += ']  '
        s += '[Cc: '
        for l in self.cclist:
            s += l['name'] + ' <' + l['email'] + '> '
        s += ']  '
        s += '[Size: ' + str(self.size) + ']}'
        return s
