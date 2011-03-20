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

from workhorse import MailBox
import model, config

model.create_entities()

for box in config.mailbox_paths:
    mb = MailBox(path=box['path'], boxtype=box['type'])
    mb.open()
    mb.load(persist=True)
    mb.close()